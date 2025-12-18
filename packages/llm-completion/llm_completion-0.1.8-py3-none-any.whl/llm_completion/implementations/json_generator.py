"""Implementation for generating data in JSON format based on schemas."""

from typing import Dict, List, Any, Optional, Union
import json
import random
import re
from urllib.parse import urlparse
import requests

from ..completion import LiteLLMCompletion
from ..logger import logger

# Import unsplash API functions
try:
    from unsplash_lite_dataset_api import (
        create_opensearch_client,
        load_opensearch_config,
        search_images,
    )
    UNSPLASH_INDEX_NAME = "unsplash_photos"
except ImportError:
    create_opensearch_client = None
    load_opensearch_config = None
    search_images = None
    UNSPLASH_INDEX_NAME = None

def merge_schemas(schemas: dict) -> dict:
    """
    Combines a list of JSON schemas into a single schema using the 'allOf' keyword.

    This is the most robust and recommended method for combining schemas, as it
    preserves the validation rules of each individual schema.

    Args:
        schemas: A list of dictionaries, where each dictionary is a JSON schema.

    Returns:
        A new dictionary representing the combined JSON schema.
    """
    merged_schema = {
        "type": "object",
        "properties": schemas,
        "additionalProperties": False
    }
    
    return merged_schema

class JsonSchemaDataGenerator:
    """Generator for JSON data based on schemas."""

    def __init__(self, completion_provider: Optional[LiteLLMCompletion] = None) -> None:
        """Initialize the JSON generator.

        Args:
            completion_provider: Optional completion provider to use. If not provided,
                a new instance will be created.
        """
        self.completion_provider = completion_provider or LiteLLMCompletion()
        self.system_prompt = (
            "You are an expert Website Copywriter specializing in creating realistic"
            " JSON data that conforms to specific schemas for the Website. Don't repeat things."
        )
        
        # Initialize OpenSearch client for image fetching
        self.opensearch_client = None
        if create_opensearch_client and load_opensearch_config:
            try:
                config = load_opensearch_config()
                self.opensearch_client = create_opensearch_client(config)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenSearch client: {e}")
                self.opensearch_client = None

    def generate_data(
        self, 
        schemas: Dict[str, Any], 
        user_prompt: str,
        num_examples: int = 1
    ) -> Dict[str, Any]:
        """Generate JSON data based on provided schemas.

        Args:
            schemas: JSON schema or list of schemas.
            user_prompt: Additional instructions for data generation.
            num_examples: Number of examples to generate.

        Returns:
            A single JSON data object with predefined keys from the schema.

        Raises:
            Exception: If data generation fails.
        """
        logger.info(f"Generating data for {len(schemas.keys())} schemas")

        # icons = {
        #     "type": "array",
        #     "items": {
        #         "type": "string"
        #     }
        # }

        # schemas["icons"] = icons

        # merged_schema = merge_schemas(schemas)
        # print("merged_schema:", merged_schema)

        
        prompt = (
            f"Generate {num_examples} examples of JSON data"
            f"Additional requirements: \n{user_prompt}\n\n"
            "We are generating data for Landing pages so repeat minimally only if required.\n"
            "Fill image assets with Unsplash/Pexels/Pixabay stock images you know exist.\n"
            "Only use known icons from `lucide-react`.\n\n"
            # "icons will contain all the icons used in the JSON data."
            "Return ONLY valid JSON data that matches the schema(s) provided."
        )

        try:
            # Define JSON schema for the response
            print("prompt:", prompt)

            result = self.completion_provider.complete_with_json(prompt, self.system_prompt, json_schema=schemas)
            print("Generated JSON data:", result)
            
            # Process the data to ensure all image and icon fields are properly formatted
            processed_result = self._process_generated_data(result)
            
            logger.info("Successfully generated data")

            return processed_result

        except Exception as e:
            logger.error(f"Failed to generate JSON data: {str(e)}")
            raise

    async def agenerate_data(
        self, 
        schemas: Dict[str, Any], 
        user_prompt: str,
        num_examples: int = 1
    ) -> Dict[str, Any]:
        """Asynchronously generate JSON data based on provided schemas.

        Args:
            schemas: JSON schema or list of schemas.
            user_prompt: Additional instructions for data generation.
            num_examples: Number of examples to generate.

        Returns:
            A single JSON data object with predefined keys from the schema.

        Raises:
            Exception: If data generation fails.
        """
        logger.info(f"Async generating data for {len(schemas.keys())} schemas")
        
        prompt = (
            f"Generate {num_examples} examples of JSON data"
            f"Additional requirements: \n{user_prompt}\n\n"
            "We are generating data for Landing pages so repeat minimally only if required.\n"
            "Fill image assets with Unsplash/Pexels/Pixabay stock images you know exists.\n"
            "Only use known icons from `lucide-react`.\n\n"
            "Return ONLY valid JSON data that matches the schema(s) provided."
        )

        try:
            result = await self.completion_provider.acomplete_with_json(prompt, self.system_prompt, json_schema=schemas)
            
            # Process the data to ensure all image and icon fields are properly formatted
            processed_result = self._process_generated_data(result)
            
            logger.info("Successfully async generated data")

            return processed_result

        except Exception as e:
            logger.error(f"Failed to async generate JSON data: {str(e)}")
            raise
            
    def _process_generated_data(self, data: Any) -> Any:
        """Process the generated data to format icons and other fields correctly.
        
        Args:
            data: The generated data structure
            
        Returns:
            Processed data structure
        """
        # Process data and transform icon names
        self._process_data_recursive(data)
        return data
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if an image URL is valid and actually exists (returns successful HTTP status).
        
        Args:
            url: The URL to validate
            
        Returns:
            True if URL exists and returns successful status, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        url = url.strip()
        if not url:
            return False
            
        # Check for common placeholder patterns first (fast check)
        placeholder_patterns = [
            r'^placeholder$',
            r'^https?://placeholder\.',
            r'^https?://example\.com',
            r'^https?://lorem\.',
            r'^data:image',
            r'^blob:',
            r'^#',
            r'^javascript:',
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not bool(parsed.scheme and parsed.netloc):
                return False
        except Exception:
            return False
        
        # Check if URL actually exists by making HTTP HEAD request
        try:
            # Use HEAD request with reasonable timeout to check if URL exists
            response = requests.head(
                url, 
                timeout=5,  # 5 second timeout
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; ImageValidator/1.0)'
                }
            )
            # Consider 2xx status codes as valid (successful responses)
            return 200 <= response.status_code < 300
        except (requests.RequestException, Exception) as e:
            logger.debug(f"URL validation failed for {url}: {e}")
            return False
    
    def _get_random_image_url(self, query: Optional[str] = None) -> Optional[str]:
        """Get an image URL from Unsplash dataset API.
        
        Args:
            query: Optional search query to find relevant images. If None, returns random image.
            
        Returns:
            Image URL or None if API is not available
        """
        if not self.opensearch_client or not search_images:
            return None
            
        try:
            # First try with the provided query
            results = search_images(
                self.opensearch_client,
                index_name=UNSPLASH_INDEX_NAME,
                query_text=query,
                size=10,  # Get multiple results to choose from
                from_=0
            )
            
            # If no results from query, try without query (random)
            if not results or len(results) == 0:
                results = search_images(
                    self.opensearch_client,
                    index_name=UNSPLASH_INDEX_NAME,
                    query_text=None,  # match_all for random
                    size=10,
                    from_=0
                )
            
            if results and len(results) > 0:
                # Randomly select one from the results instead of taking the first
                img_data = random.choice(results)
                return img_data.get("photo_image_url", "")
                
        except Exception as e:
            logger.warning(f"Failed to fetch image: {e}")
            
        return None
    
    def _process_data_recursive(self, data):
        """
        Recursively process data structure to find and update icon names and image sources.
        
        Args:
            data: Any data structure (dict, list, etc.) to process
        """
        if isinstance(data, dict):
            # Check for image src fields and fill if empty
            image_keys = ['src', 'imageSrc', 'imgsrc', 'image', 'img', 'url']
            for key in image_keys:
                if key in data:
                    current_value = data[key]
                    # Check if the current value is empty/invalid
                    is_empty = (
                        current_value is None or 
                        current_value == "" or 
                        current_value == "placeholder" or
                        not self._is_valid_image_url(current_value)
                    )
                    
                    if is_empty:
                        # Use alt text as search query if available
                        search_query = None
                        if 'alt' in data and data['alt'] and isinstance(data['alt'], str) and data['alt'].strip():
                            search_query = data['alt'].strip()
                        
                        random_url = self._get_random_image_url(search_query)
                        if random_url:
                            data[key] = random_url
                            logger.info(f"Filled empty/invalid image field '{key}' with URL (query: '{search_query or 'random'}')")
            
            # Check if this dict matches the Icon interface
            if (data.get('package') == 'lucide' and 
                data.get('type') == 'icon' and 
                'name' in data and 
                isinstance(data['name'], str)):
                # Transform hyphenated icon names to title case (e.g., "check-circle" -> "CheckCircle")
                icon_name = data['name']
                data['name'] = ''.join(x.title() for x in icon_name.split('-'))
            
            # Process all values
            for value in data.values():
                self._process_data_recursive(value)
                
        elif isinstance(data, list):
            # Process all list items
            for item in data:
                self._process_data_recursive(item)
    