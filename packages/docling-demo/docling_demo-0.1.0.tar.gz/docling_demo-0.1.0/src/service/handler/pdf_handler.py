from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import DocumentStream
from docling.datamodel.pipeline_options import VlmPipelineOptions, RapidOcrOptions, PdfPipelineOptions, PictureDescriptionApiOptions
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from utils.is_gibberish import is_gibberish_check
from fitz import Document
from pathlib import Path, PurePath
import fitz
import os
from utils.llm_connection import slm_connection_instance, llm_connection_instance
import base64
from io import BytesIO
from typing import Union
import logging

class DoclingPDFHandler:
    """Handle PDF"""
    def __init__(self, vlm_options: ApiVlmOptions | None = None):
        self.logger = logging.getLogger(__name__)
        if vlm_options is not None:
            self.vlm_options = vlm_options
        else:
            self.vlm_options = self._create_azure_openai_vlm_options(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                prompt="Read the image as OCR specialist, and give me exact wordings that is written or shown if there is chart, diagram, flowchart, design, please make sense of it and how it's realatable is each other and what all components are there, how they are inter connected"
            )
    
    def _create_azure_openai_vlm_options(self, azure_endpoint: str, api_key: str, 
                                         deployment_name: str, api_version: str,
                                         prompt: str = "Describe this image in a few sentences."):
        
        url = f"{azure_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        
        options = ApiVlmOptions(
            url=url,
            params=dict(),
            headers={
                "api-key": api_key,
                "Content-Type": "application/json"
            },
            prompt=prompt,
            timeout=90,
            scale=2.0,
            temperature=1.0,
            response_format=ResponseFormat.MARKDOWN,
        )
        return options
    
    def extract(self, file_path: Union[str, PurePath, Document], processing_strategy: str):
        """
        Extract text from PDF
        Returns: (docling_result, text) tuple for chunking
        """
        if processing_strategy == "text_extraction":
            return self.process_pdf_without_ocr(file_path)
        elif processing_strategy == "ocr_with_vlm":
            return self.process_pdf_with_ocr(file_path)
        else:
            return self.process_pdf_without_ocr(file_path)

    def process_pdf_without_ocr(self, source: Union[Path, str, Document ]):
        """
        Process a text-based PDF without OCR.
        Supports:
        - Path to a PDF file
        - String path to a PDF file
        - In-memory Document object (PDF only)

        Notes:
        - Scanned/image-only PDFs are NOT supported (OCR is disabled).
        """
        self.logger.info("Processing PDF without OCR.")
        if isinstance(source, Document):
            bytes_io = source.write()
            source = DocumentStream(name="document.pdf", stream=BytesIO(bytes_io))
        elif isinstance(source, str):
            source = Path(source)
        elif isinstance(source, Path):
            source = source
        else:
            raise TypeError("source must be Str or Path or Document")
        
        picture_description_remote_vlm_options = PictureDescriptionApiOptions(
            **self.vlm_options.model_dump()
            )
        
        ocr_pdf_pipeline = PdfPipelineOptions(
            enable_remote_services=True,
            do_ocr=False,
            do_table_structure=True,
            do_picture_description=True,
            picture_description_options=picture_description_remote_vlm_options
        )

        ocr_pdf_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=ocr_pdf_pipeline)
            }
        )
        try:
            ocr_result = ocr_pdf_converter.convert(source=source)
            ocr_text = ocr_result.document.export_to_markdown()
            return ocr_result, ocr_text         
        except Exception as e:
            self.logger.exception(f"Error processing PDF without OCR: {e}")
            raise

    def process_pdf_with_ocr(self, source: Union[Path, str, Document]):

        if isinstance(source, Document):
            bytes_io = source.write()
            source = DocumentStream(name="document.pdf", stream=BytesIO(bytes_io))
        elif isinstance(source, str):
            source = Path(source)
        elif isinstance(source, Path):
            source = source
        else:
            raise TypeError("source must be Str or Path or Document")
        
        ocr_option_pipelines = PdfPipelineOptions(
            images_scale=1,
            do_ocr=True,
            ocr_options=RapidOcrOptions(force_full_page_ocr=True)
        )
        
        ocr_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=ocr_option_pipelines)
            }
        )
        
        ocr_result = ocr_converter.convert(source=source)
        ocr_text = ocr_result.document.export_to_text()
        
        score = is_gibberish_check(text=ocr_text)
        print(f"Quality score: {score}")
        
        if score >= 0.45:
            return ocr_result, ocr_text
        else:
            return self.process_pdf_with_vlm(source)

    def process_pdf_with_vlm(self, source: Union[Path, str, Document]):

        if isinstance(source, Document):
            bytes_io = source.write()
            source = DocumentStream(name="document.pdf", stream=BytesIO(bytes_io))
        elif isinstance(source, str):
            source = Path(source)
        elif isinstance(source, Path):
            source = source
        else:
            raise TypeError("source must be Str or Path or Document")

        picture_description_options = PictureDescriptionApiOptions(
            vlm_options=self.vlm_options,
            prompt=self.vlm_options.prompt
        )

        vlm_pipeline = VlmPipelineOptions(
            enable_remote_services=True,
            images_scale=1,
            generate_picture_images=True,
            picture_description_options=picture_description_options,
            vlm_options=self.vlm_options
        ) 

        vlm_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=vlm_pipeline, 
                                                 pipeline_cls=VlmPipeline)
            }
        )

        vlm_result = vlm_converter.convert(source=source)
        vlm_text = vlm_result.document.export_to_markdown()

        return vlm_result, vlm_text  