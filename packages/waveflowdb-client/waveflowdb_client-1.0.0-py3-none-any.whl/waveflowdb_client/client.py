import time
import logging
import json
import requests
import os
from typing import List, Optional, Dict, Any

from .config import Config
from .utils import FileProcessor, Logger, BatchManager
from .exceptions import APIError, FileProcessingError
from .models import HealthResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VectorLakeClient:
    def __init__(self, config: Optional[Config] = None, **kwargs):
        if config is None:
            config = Config(**kwargs)
        logging.info(f"Initializing VectorLakeClient with base_url={config.base_url_query}")
        self.config = config
        self.logger = Logger(config.log_dir)
        self.batch_manager = BatchManager(config.max_files_per_batch, config.max_batch_size_mb)
        self.file_processor = FileProcessor()

    def _get_headers(self) -> Dict[str, str]:
        return {'Content-Type': 'application/json', 'x-api-key': self.config.api_key}

    def _make_request(self, endpoint: str, payload: Dict[str, Any], operation: str = "", batch_num: int = 0) -> Dict[str, Any]:
        headers = self._get_headers()
        request_size = len(json.dumps(payload).encode('utf-8')) / 1024 if payload else 0

        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                response = requests.post(endpoint, json=payload, headers=headers, timeout=self.config.timeout)
                latency = (time.time() - start_time) * 1000

                try:
                    result = response.json()
                except Exception:
                    result = {"status_code": response.status_code, "text": response.text}

                if operation:
                    response_size = len(response.content) / 1024 if response.content else 0
                    result_count = len(result.get("results", [])) if isinstance(result, dict) else "N/A"
                    self.logger.log_performance(
                        operation=operation,
                        batch_num=batch_num,
                        latency=latency,
                        request_size=request_size,
                        response_size=response_size,
                        result_count=result_count
                    )

                if response.status_code >= 400:
                    raise APIError(result.get('message', f'HTTP {response.status_code}'), status_code=response.status_code, response_text=response.text)

                return result

            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    error_msg = f"Request failed after {self.config.max_retries} attempts: {str(e)}"
                    if operation:
                        self.logger.log_api_error(operation, batch_num, error_msg)
                    raise APIError(error_msg, getattr(e.response, 'status_code', None), getattr(e.response, 'text', None))
                time.sleep(2 ** attempt)

    def _make_request_with_backoff(self, endpoint, payload, operation, batch_num, retries=5, base_delay=1):
        delay = base_delay
        for attempt in range(retries):
            try:
                return self._make_request(endpoint, payload, operation, batch_num)
            except APIError as e:
                if getattr(e, "status_code", None) == 429:
                    logging.warning(f"Batch {batch_num} throttled, retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
            except Exception:
                raise

    def _read_files(self, filenames: List[str], chunks_dir: Optional[str] = None) -> List[str]:
        """
        Reads files safely. If chunks_dir is provided, reads files from that folder.
        """
        contents = []
        for fname in filenames:
            path_base = chunks_dir if chunks_dir else self.config.vector_lake_path
            filepath = os.path.join(path_base, fname)
            try:
                if self.file_processor.is_supported_file(fname):
                    content = self.file_processor.read_file_content(filepath)
                    contents.append(content)
                else:
                    self.logger.log_skipped_file(fname, "Unsupported file type")
                    contents.append("")
            except Exception as e:
                self.logger.log_skipped_file(fname, f"Read error: {str(e)}")
                contents.append("")
        return contents

    def get_matching_docs(self,
                          query: str,
                          user_id: str,
                          vector_lake_description: str,
                          pattern: str = "static",
                          session_id: Optional[str] = None,
                          hybrid_filter: bool = False,
                          top_docs: int = 10,
                          threshold: float = 0.2,
                          files: Optional[List[str]] = None,
                          files_name: Optional[List[str]] = None,
                          files_data: Optional[List[str]] = None,
                          with_data: bool = False) -> Dict[str, Any]:

        endpoint_key = "top_matching_docs_with_data" if with_data else "top_matching_docs"
        endpoint = self.config.endpoints[endpoint_key]

        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "vector_lake_description": vector_lake_description,
            "query": query,
            "hybrid_filter": hybrid_filter,
            "top_docs": top_docs,
            "threshold": threshold,
            "pattern": pattern
        }

        # Direct mode
        if files_name and files_data:
            if len(files_name) != len(files_data):
                raise ValueError("files_name and files_data must be same length")
            clean_names = [os.path.basename(n) for n in files_name]
            payload.update({"files_name": clean_names, "files_data": files_data, "pattern": "dynamic"})
            return self._make_request(endpoint, payload, endpoint_key)

        # Dynamic mode: read from filesystem
        if pattern == "dynamic" and files:
            batches, chunks_dir = self.batch_manager.create_batches(files, self.config.vector_lake_path)
            flat_files = [fname for batch in batches for fname in batch]
            file_contents = self._read_files(flat_files, chunks_dir)
            payload.update({"files_name": flat_files, "files_data": file_contents, "pattern": "dynamic"})
            return self._make_request(endpoint, payload, endpoint_key)

        # Static mode
        return self._make_request(endpoint, payload, endpoint_key)

    def add_documents(self,
                      user_id: str,
                      vector_lake_description: str,
                      start_from_batch=1,
                      intelligent_segmentation: bool = True,
                      session_id: Optional[str] = None,
                      files: Optional[List[str]] = None,
                      files_name: Optional[List[str]] = None,
                      files_data: Optional[List[str]] = None,
                      max_workers=5) -> Any:
        """
        Add documents either in direct mode (names + data) or batch mode (filesystem).
        """
        # Direct mode
        if files_name and files_data:
            if len(files_name) != len(files_data):
                raise ValueError("files_name and files_data must be same length")
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "vector_lake_description": vector_lake_description,
                "files_name": [os.path.basename(n) for n in files_name],
                "files_data": files_data,
                "intelligent_segmentation": intelligent_segmentation
            }
            endpoint = self.config.endpoints["add_docs"]
            return self._make_request(endpoint, payload, "add_docs", batch_num=1)

        # Batch mode
        return self._process_files_in_batches(
            "add_docs", user_id, vector_lake_description, start_from_batch,
            intelligent_segmentation, session_id, files, max_workers=max_workers
        )

    def refresh_documents(self,
                          user_id: str,
                          vector_lake_description: str,
                          start_from_batch=1,
                          intelligent_segmentation: bool = True,
                          session_id: Optional[str] = None,
                          files: Optional[List[str]] = None,
                          files_name: Optional[List[str]] = None,
                          files_data: Optional[List[str]] = None,
                          max_workers=5) -> Any:
        """
        Same semantics as add_documents
        """
        if files_name and files_data:
            if len(files_name) != len(files_data):
                raise ValueError("files_name and files_data must be same length")
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "vector_lake_description": vector_lake_description,
                "files_name": [os.path.basename(n) for n in files_name],
                "files_data": files_data,
                "intelligent_segmentation": intelligent_segmentation
            }
            endpoint = self.config.endpoints["refresh_docs"]
            return self._make_request(endpoint, payload, "refresh_docs", batch_num=1)

        return self._process_files_in_batches(
            "refresh_docs", user_id, vector_lake_description, start_from_batch,
            intelligent_segmentation, session_id, files, max_workers=max_workers
        )

    def health_check(
        self,
        user_id: str,
        vector_lake_description: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        endpoint = self.config.endpoints["health"]

        payload = {
            "user_id": user_id,
            "vector_lake_description": vector_lake_description,
            "session_id": session_id
        }

        try:
            result = self._make_request(
                endpoint=endpoint,
                payload=payload,
                operation="health"
            )

            return result
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }

    def _process_files_in_batches(self, operation: str, user_id: str, vector_lake_description: str,
                              start_from_batch: int = 1, intelligent_segmentation: bool = False,
                              session_id: Optional[str] = None, files: Optional[List[str]] = None,
                              max_workers: int = 5, batch_delay: float = 2) -> dict:
        """
        Processes files from the filesystem in batches using BatchManager.
        Returns a standardized envelope.
        """
        base_path = self.config.vector_lake_path

        # 1. Gather files if not provided
        if files is None:
            files = [f for f in os.listdir(base_path)
                    if os.path.isfile(os.path.join(base_path, f)) and self.file_processor.is_supported_file(f)]

        # 2. Create batches using BatchManager
        batches, chunks_dir = self.batch_manager.create_batches(files, base_path)
        logging.info(f"Batches created: {batches}, chunks_dir: {chunks_dir}")

        batch_outputs = []
        start_index = start_from_batch - 1
        endpoint = self.config.endpoints[operation]

        for i, batch in enumerate(batches):
            batch_num = i + 1

            # Skip batches if resuming
            if i < start_index:
                logging.info(f"Skipping batch {batch_num}")
                continue

            start_time = time.time()

            try:
                # 3. Read file contents from chunks folder
                file_contents = []
                for fname in batch:
                    full_path = os.path.join(chunks_dir, fname)
                    if not os.path.exists(full_path):
                        full_path = os.path.join(base_path, fname)
                    content = self.file_processor.read_file_content(full_path)
                    file_contents.append(content)

                payload = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "vector_lake_description": vector_lake_description,
                    "files_name": batch,      # API expects basenames
                    "files_data": file_contents,
                    "intelligent_segmentation": intelligent_segmentation
                }
                # logging.info(f"payload is {payload}")  
                 # 4. Make request with backoff
                result = self._make_request_with_backoff(endpoint, payload, operation, batch_num)

                processing_time = time.time() - start_time
                logging.info(f"Batch {batch_num} done")

                batch_outputs.append({
                    "batch_number": batch_num,
                    "files": batch,
                    "success": True,
                    "processing_time": round(processing_time, 3),
                    "response": result
                })

            except Exception as e:
                processing_time = time.time() - start_time
                logging.error(f"Batch {batch_num} failed: {str(e)}")
                batch_outputs.append({
                    "batch_number": batch_num,
                    "files": batch,
                    "success": False,
                    "processing_time": round(processing_time, 3),
                    "response": None,
                    "error": str(e)
                })

            # 5. Delay between batches
            time.sleep(batch_delay)

        return {
            "mode": "batch",
            "total_batches": len(batches),
            "batches": sorted(batch_outputs, key=lambda x: x["batch_number"])
        }
    
    def get_namespace_details(self, user_id: str, session_id: Optional[str] = None, vector_lake_description: Optional[str] = None) -> Dict[str, Any]:
        endpoint = self.config.endpoints["get_namespace_details_by_userid"]
        payload = {"session_id": session_id, "user_id": user_id}
        if vector_lake_description:
            payload["vector_lake_description"] = vector_lake_description
        try:
            result = self._make_request(endpoint, payload, "get_namespace_details")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_docs_information(self, user_id: str, vector_lake_description: str, session_id: Optional[str] = None, keyword: Optional[str] = None, threshold: int = 70) -> Dict[str, Any]:
        endpoint = self.config.endpoints["get_docs_information"]
        payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description, "threshold": threshold}
        if keyword:
            payload["keyword"] = keyword
        try:
            result = self._make_request(endpoint, payload, "get_docs_information")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def full_corpus_search(self, user_id: str, vector_lake_description: str, keyword: str, session_id: Optional[str] = None, top_docs: int = 10) -> Dict[str, Any]:
        endpoint = self.config.endpoints["full_corpus_search"]
        payload = {"session_id": session_id, "user_id": user_id, "vector_lake_description": vector_lake_description, "keyword": keyword, "top_docs": top_docs}
        try:
            result = self._make_request(endpoint, payload, "full_corpus_search")
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
