#!/usr/bin/env python3
"""
ArXiv MCP Server

A Model Context Protocol (MCP) server that provides access to arXiv papers.
Supports searching papers, getting metadata, and extracting paper content.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import io
import re

import aiohttp
import PyPDF2
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arxiv-mcp-server")

class ArxivMCPServer:
    def __init__(self):
        self.app = Server("arxiv-mcp-server")
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "http://export.arxiv.org/api/query"
        self.pdf_cache = {}  # Simple in-memory cache for PDF content
        
        # Register handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.app.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="arxiv://search",
                    name="ArXiv Paper Search",
                    description="Search for papers on arXiv",
                    mimeType="application/json"
                ),
                Resource(
                    uri="arxiv://categories",
                    name="ArXiv Categories",
                    description="List of arXiv subject categories",
                    mimeType="application/json"
                )
            ]
        
        @self.app.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific resource"""
            if uri == "arxiv://search":
                return json.dumps({
                    "description": "Use the search_papers tool to find papers",
                    "example": "search_papers with query='machine learning'"
                })
            elif uri == "arxiv://categories":
                return json.dumps(self._get_arxiv_categories())
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.app.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="search_papers",
                    description="Search for papers on arXiv by query, author, category, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (keywords, title, etc.)"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author name (optional)"
                            },
                            "category": {
                                "type": "string",
                                "description": "arXiv category (e.g., cs.AI, math.GT)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": ["relevance", "lastUpdatedDate", "submittedDate"],
                                "description": "Sort order",
                                "default": "relevance"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_paper_details",
                    description="Get detailed information about a specific paper by arXiv ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "arxiv_id": {
                                "type": "string",
                                "description": "arXiv paper ID (e.g., 2301.07041)"
                            }
                        },
                        "required": ["arxiv_id"]
                    }
                ),
                Tool(
                    name="get_paper_content",
                    description="Extract and return the text content of a paper's PDF",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "arxiv_id": {
                                "type": "string",
                                "description": "arXiv paper ID (e.g., 2301.07041)"
                            },
                            "max_pages": {
                                "type": "integer",
                                "description": "Maximum number of pages to extract (default: 20)",
                                "default": 20
                            }
                        },
                        "required": ["arxiv_id"]
                    }
                ),
                Tool(
                    name="summarize_paper",
                    description="Get a summary of a paper including abstract and key information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "arxiv_id": {
                                "type": "string",
                                "description": "arXiv paper ID (e.g., 2301.07041)"
                            }
                        },
                        "required": ["arxiv_id"]
                    }
                )
            ]
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "search_papers":
                    return await self._search_papers(**arguments)
                elif name == "get_paper_details":
                    return await self._get_paper_details(**arguments)
                elif name == "get_paper_content":
                    return await self._get_paper_content(**arguments)
                elif name == "summarize_paper":
                    return await self._summarize_paper(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _ensure_session(self):
        """Ensure we have an active aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _search_papers(self, query: str, author: str = None, category: str = None, 
                           max_results: int = 10, sort_by: str = "relevance") -> List[TextContent]:
        """Search for papers on arXiv"""
        await self._ensure_session()
        
        # Build search query
        search_terms = []
        
        if query:
            search_terms.append(f"all:{quote_plus(query)}")
        
        if author:
            search_terms.append(f"au:{quote_plus(author)}")
        
        if category:
            search_terms.append(f"cat:{category}")
        
        search_query = " AND ".join(search_terms)
        
        # API parameters
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max_results, 100),  # arXiv API limit
            "sortBy": sort_by,
            "sortOrder": "descending"
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            if response.status != 200:
                raise Exception(f"arXiv API error: {response.status}")
            
            content = await response.text()
            papers = self._parse_arxiv_response(content)
            
            if not papers:
                return [TextContent(type="text", text="No papers found matching your query.")]
            
            # Format results
            result = f"Found {len(papers)} papers:\n\n"
            for i, paper in enumerate(papers, 1):
                result += f"{i}. **{paper['title']}**\n"
                result += f"   Authors: {', '.join(paper['authors'])}\n"
                result += f"   arXiv ID: {paper['id']}\n"
                result += f"   Published: {paper['published']}\n"
                result += f"   Categories: {', '.join(paper['categories'])}\n"
                result += f"   Abstract: {paper['summary'][:200]}...\n"
                result += f"   URL: {paper['link']}\n\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _get_paper_details(self, arxiv_id: str) -> List[TextContent]:
        """Get detailed information about a specific paper"""
        await self._ensure_session()
        
        # Clean arxiv_id (remove version if present)
        clean_id = arxiv_id.split('v')[0]
        
        params = {
            "id_list": clean_id,
            "max_results": 1
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            if response.status != 200:
                raise Exception(f"arXiv API error: {response.status}")
            
            content = await response.text()
            papers = self._parse_arxiv_response(content)
            
            if not papers:
                return [TextContent(type="text", text=f"Paper with ID {arxiv_id} not found.")]
            
            paper = papers[0]
            
            # Format detailed information
            result = f"**{paper['title']}**\n\n"
            result += f"**arXiv ID:** {paper['id']}\n"
            result += f"**Authors:** {', '.join(paper['authors'])}\n"
            result += f"**Published:** {paper['published']}\n"
            result += f"**Updated:** {paper['updated']}\n"
            result += f"**Categories:** {', '.join(paper['categories'])}\n"
            result += f"**URL:** {paper['link']}\n"
            result += f"**PDF:** {paper['pdf_url']}\n\n"
            result += f"**Abstract:**\n{paper['summary']}\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _get_paper_content(self, arxiv_id: str, max_pages: int = 20) -> List[TextContent]:
        """Extract text content from paper PDF"""
        await self._ensure_session()
        
        # Check cache first
        cache_key = f"{arxiv_id}_{max_pages}"
        if cache_key in self.pdf_cache:
            return [TextContent(type="text", text=self.pdf_cache[cache_key])]
        
        # Clean arxiv_id
        clean_id = arxiv_id.split('v')[0]
        pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        
        try:
            async with self.session.get(pdf_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download PDF: {response.status}")
                
                pdf_data = await response.read()
                
                # Extract text from PDF
                text_content = self._extract_pdf_text(pdf_data, max_pages)
                
                # Cache the result
                self.pdf_cache[cache_key] = text_content
                
                return [TextContent(type="text", text=text_content)]
                
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            return [TextContent(type="text", text=f"Error extracting PDF content: {str(e)}")]
    
    async def _summarize_paper(self, arxiv_id: str) -> List[TextContent]:
        """Get a summary of the paper"""
        # Get paper details first
        details = await self._get_paper_details(arxiv_id)
        
        if not details or "not found" in details[0].text.lower():
            return details
        
        # Try to get a bit of the content for additional context
        try:
            content = await self._get_paper_content(arxiv_id, max_pages=3)
            if content and len(content[0].text) > 1000:
                # Extract first few paragraphs
                text = content[0].text
                paragraphs = text.split('\n\n')[:5]  # First 5 paragraphs
                intro_text = '\n\n'.join(paragraphs)
                
                summary = details[0].text + f"\n\n**Introduction/Content Preview:**\n{intro_text[:1500]}..."
                return [TextContent(type="text", text=summary)]
        except:
            pass
        
        return details
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv API XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {}
                
                # Basic information
                paper['id'] = entry.find('atom:id', ns).text.split('/')[-1]
                paper['title'] = entry.find('atom:title', ns).text.strip()
                paper['summary'] = entry.find('atom:summary', ns).text.strip()
                paper['published'] = entry.find('atom:published', ns).text
                paper['updated'] = entry.find('atom:updated', ns).text
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                paper['authors'] = authors
                
                # Categories
                categories = []
                for category in entry.findall('atom:category', ns):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                paper['categories'] = categories
                
                # Links
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        paper['pdf_url'] = link.get('href')
                    elif link.get('rel') == 'alternate':
                        paper['link'] = link.get('href')
                
                papers.append(paper)
                
        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {str(e)}")
            
        return papers
    
    def _extract_pdf_text(self, pdf_data: bytes, max_pages: int) -> str:
        """Extract text from PDF data"""
        try:
            pdf_file = io.BytesIO(pdf_data)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            num_pages = min(len(reader.pages), max_pages)
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespaces
                text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines
                
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")
            
            result = '\n'.join(text_parts)
            
            if len(result) < 100:
                return "Warning: Extracted text is very short. PDF might be image-based or have extraction issues.\n\n" + result
            
            return result
            
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    def _get_arxiv_categories(self) -> Dict[str, List[str]]:
        """Return arXiv subject categories"""
        return {
            "Computer Science": [
                "cs.AI - Artificial Intelligence",
                "cs.CL - Computation and Language",
                "cs.CV - Computer Vision and Pattern Recognition",
                "cs.LG - Machine Learning",
                "cs.NE - Neural and Evolutionary Computing",
                "cs.RO - Robotics"
            ],
            "Mathematics": [
                "math.AG - Algebraic Geometry",
                "math.GT - Geometric Topology",
                "math.LO - Logic",
                "math.NT - Number Theory",
                "math.ST - Statistics Theory"
            ],
            "Physics": [
                "physics.comp-ph - Computational Physics",
                "physics.data-an - Data Analysis, Statistics and Probability",
                "quant-ph - Quantum Physics"
            ],
            "Statistics": [
                "stat.AP - Applications",
                "stat.CO - Computation",
                "stat.ML - Machine Learning",
                "stat.TH - Theory"
            ]
        }
    
    async def run(self):
        """Run the MCP server"""
        # Setup initialization options
        init_options = InitializationOptions(
            server_name="arxiv-mcp-server",
            server_version="1.0.0",
            capabilities={
                "resources": {},
                "tools": {},
                "prompts": {},
                "logging": {}
            }
        )
        
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                init_options
            )

async def main():
    """Main entry point"""
    server = ArxivMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())