#!/usr/bin/env python3
"""
HTTP/HTTPS MCP Server for ServiceNex

This exposes the MCP server functionality over HTTP/HTTPS using FastAPI.
Can be deployed to Cloud Run or any HTTP hosting service.
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.mcp_server import server
from app.config import MY_API_BASE_URL, MY_API_KEY
from app.loaders.my_api_loader import fetch_tickets, fetch_articles, fetch_ticket_by_id, fetch_ticket_comments, fetch_articles_by_ticket_id, get_suggested_next_steps, generate_suggested_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any]


class ResourceReadRequest(BaseModel):
    uri: str


# Global server instance
mcp_server = server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    logger.info("Starting HTTP MCP Server...")
    yield
    logger.info("Shutting down HTTP MCP Server...")


# Create FastAPI app
app = FastAPI(
    title="ServiceNex MCP Server",
    description="HTTP/HTTPS interface for ServiceNex MCP tools and resources",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_api_key_from_header(request: Request) -> Optional[str]:
    """Extract API key from request headers."""
    # Check Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    # Check X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key
    
    # Check X-ServiceNex-API-Key header
    api_key = request.headers.get("X-ServiceNex-API-Key")
    if api_key:
        return api_key
    
    return None


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "ServiceNex MCP Server",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    Server-Sent Events endpoint for MCP over HTTP transport.
    This allows Claude Desktop (newer versions) to connect via HTTP/SSE.
    """
    async def event_generator():
        """Generate SSE events for MCP protocol."""
        try:
            # Send initial connection event
            yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
            
            # Keep connection alive
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/mcp/tools")
async def list_tools(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """List available MCP tools."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Return hardcoded tools list (matching MCP server tools)
        return {
            "tools": [
                {
                    "name": "get_knowledge_articles",
                    "description": "Fetch knowledge base articles from ServiceNex. Returns published articles with title, category, author, and status information. Supports pagination and category filtering.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category name (default: 'all' for all categories)",
                                "default": "all"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number for pagination (default: 1)",
                                "default": 1
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of articles per page (default: 10)",
                                "default": 10
                            }
                        }
                    }
                },
                {
                    "name": "get_tickets",
                    "description": "Fetch recent support tickets from ServiceNex. Returns ticket information including titles and status. Supports pagination and category filtering.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by category name (default: 'all' for all categories)",
                                "default": "all"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number for pagination (default: 1)",
                                "default": 1
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of tickets per page (default: 5)",
                                "default": 5
                            }
                        }
                    }
                },
                {
                    "name": "search_articles",
                    "description": "Search for specific knowledge base articles by keyword or topic.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant articles"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_article_by_id",
                    "description": "Get detailed information about a specific article by its ID.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "article_id": {
                                "type": "string",
                                "description": "The ID of the article to retrieve"
                            }
                        },
                        "required": ["article_id"]
                    }
                },
                {
                    "name": "get_ticket_by_id",
                    "description": "Get detailed information about a specific support ticket by its ID.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to retrieve"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                },
                {
                    "name": "get_articles_for_ticket",
                    "description": "List knowledge base articles related to a specific ticket ID. First fetches the ticket by ID, then searches articles based on the ticket's title (subject), description, and category. Returns articles sorted by relevance score.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to get related articles for"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                },
                {
                    "name": "get_suggested_next_steps",
                    "description": "Get suggested next steps for resolving a ticket based on related knowledge base articles. Extracts actionable steps, troubleshooting procedures, and recommendations from article content. Returns a numbered list of steps with titles and descriptions.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to get suggested next steps for"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                },
                {
                    "name": "get_ticket_comments",
                    "description": "Get all comments for a specific ticket ID. Returns all comments associated with the ticket including author, timestamp, and comment content.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to get comments for"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                },
                {
                    "name": "get_suggested_response",
                    "description": "Generate a suggested response for a ticket by analyzing the ticket details, all comments, and related knowledge base articles. Includes sentiment analysis to adjust the response tone (empathetic for negative sentiment, professional for neutral/positive). Returns a professional customer-facing response with troubleshooting steps.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ID of the ticket to generate a suggested response for"
                            }
                        },
                        "required": ["ticket_id"]
                    }
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/call")
async def call_tool(
    tool_request: ToolCallRequest,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Call an MCP tool."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Route to appropriate function based on tool name
        if tool_request.name == "get_tickets":
            result = fetch_tickets(
                category=tool_request.arguments.get("category", "all"),
                page=tool_request.arguments.get("page", 1),
                limit=tool_request.arguments.get("limit", 5)
            )
            return {
                "tool": tool_request.name,
                "content": [{"type": "text", "text": str(result)}]
            }
        
        elif tool_request.name == "get_knowledge_articles":
            result = fetch_articles(
                category=tool_request.arguments.get("category", "all"),
                page=tool_request.arguments.get("page", 1),
                limit=tool_request.arguments.get("limit", 10)
            )
            return {
                "tool": tool_request.name,
                "content": [{"type": "text", "text": str(result)}]
            }
        
        elif tool_request.name == "search_articles":
            query = tool_request.arguments.get("query", "").lower()
            if not query:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a search query"}]
                }
            result = fetch_articles(category="all", page=1, limit=50)
            # Simple search filter
            if isinstance(result, dict) and "articles" in result:
                articles = result["articles"]
                filtered_articles = [
                    article for article in articles
                    if query in article.get('title', '').lower() or
                       query in article.get('categoryName', '').lower()
                ]
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": str(filtered_articles[:10])}]
                }
        
        elif tool_request.name == "get_article_by_id":
            article_id = tool_request.arguments.get("article_id")
            if not article_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide an article ID"}]
                }
            result = fetch_articles(category="all", page=1, limit=100)
            if isinstance(result, dict) and "articles" in result:
                articles = result["articles"]
                article = next(
                    (a for a in articles if str(a.get('id')) == str(article_id)),
                    None
                )
                if article:
                    return {
                        "tool": tool_request.name,
                        "content": [{"type": "text", "text": str(article)}]
                    }
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Article with ID '{article_id}' not found"}]
                }
        
        elif tool_request.name == "get_ticket_by_id":
            ticket_id = tool_request.arguments.get("ticket_id")
            if not ticket_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a ticket ID"}]
                }
            try:
                ticket = fetch_ticket_by_id(ticket_id)
                if ticket:
                    # Format ticket details
                    response_text = f"🎫 ServiceNex Support Ticket Details\n"
                    response_text += f"{'=' * 50}\n\n"
                    response_text += f"Subject: {ticket.get('subject', 'No Subject')}\n"
                    response_text += f"{'─' * 50}\n"
                    response_text += f"Ticket #: {ticket.get('ticketNumber', 'N/A')}\n"
                    response_text += f"ID: {ticket.get('id', ticket_id)}\n"
                    response_text += f"Type: {ticket.get('typeName', 'N/A')}\n"
                    response_text += f"Status: {ticket.get('status', 'Unknown')}\n"
                    response_text += f"Priority: {ticket.get('priority', 'Unknown')}\n"
                    response_text += f"Customer: {ticket.get('customerName', 'N/A')}\n"
                    response_text += f"Assignee ID: {ticket.get('assigneeId', 'Unassigned')}\n"
                    response_text += f"Created: {ticket.get('createdAt', 'N/A')}\n"
                    response_text += f"Updated: {ticket.get('updatedAt', 'N/A')}\n"
                    description = ticket.get('description', 'No description available')
                    response_text += f"\nDescription:\n{'-' * 50}\n{description}\n"
                    
                    return {
                        "tool": tool_request.name,
                        "content": [{"type": "text", "text": response_text}]
                    }
                else:
                    return {
                        "tool": tool_request.name,
                        "content": [{"type": "text", "text": f"Ticket with ID '{ticket_id}' not found"}]
                    }
            except Exception as e:
                logger.error(f"Error fetching ticket by ID: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Error fetching ticket: {str(e)}"}]
                }
        
        elif tool_request.name == "get_articles_for_ticket":
            ticket_id = tool_request.arguments.get("ticket_id")
            if not ticket_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a ticket ID"}]
                }
            try:
                results = fetch_articles_by_ticket_id(ticket_id)
                
                # Handle response format
                if isinstance(results, dict):
                    articles = results.get("articles", [])
                    total = results.get("total", len(articles))
                    ticket_subject = results.get("ticket_subject", "N/A")
                    search_criteria = results.get("search_criteria", {})
                elif isinstance(results, list):
                    articles = results
                    total = len(articles)
                    ticket_subject = "N/A"
                    search_criteria = {}
                else:
                    articles = []
                    total = 0
                    ticket_subject = "N/A"
                    search_criteria = {}
                
                # Format the response
                response_text = f"📚 Knowledge Base Articles for Ticket #{ticket_id}\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Ticket Subject: {ticket_subject}\n"
                if search_criteria.get("category"):
                    response_text += f"Ticket Category: {search_criteria.get('category')}\n"
                response_text += f"\nFound {total} relevant article(s)\n\n"
                
                if articles and len(articles) > 0:
                    for idx, article in enumerate(articles, 1):
                        title = article.get('title', 'Untitled')
                        category_name = article.get('categoryName', article.get('category', 'Uncategorized'))
                        summary = article.get('summary', 'No summary available')
                        content = article.get('content', 'No content available')
                        match_score = article.get('_match_score', 0)
                        match_reasons = article.get('_match_reasons', [])
                        
                        response_text += f"{idx}. {title}\n"
                        response_text += f"   {'─' * 50}\n"
                        response_text += f"   Category: {category_name}\n"
                        response_text += f"   Summary: {summary}\n"
                        if match_score > 0:
                            response_text += f"   Relevance Score: {match_score} ({', '.join(match_reasons)})\n"
                        response_text += f"\n   Content:\n"
                        response_text += f"   {'─' * 50}\n"
                        # Strip HTML tags for cleaner display (basic approach)
                        content_text = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
                        content_text = content_text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                        # Limit content length for readability
                        if len(content_text) > 1000:
                            content_text = content_text[:1000] + "...\n   [Content truncated - full content available in article]"
                        # Indent each line of content
                        content_lines = content_text.split('\n')
                        for line in content_lines:
                            if line.strip():
                                response_text += f"   {line}\n"
                        response_text += "\n"
                else:
                    response_text += "No relevant articles found based on ticket title, description, and category.\n"
                
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": response_text}]
                }
            except Exception as e:
                logger.error(f"Error fetching articles for ticket: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Error fetching articles for ticket: {str(e)}"}]
                }
        
        elif tool_request.name == "get_suggested_next_steps":
            ticket_id = tool_request.arguments.get("ticket_id")
            if not ticket_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a ticket ID"}]
                }
            try:
                result = get_suggested_next_steps(ticket_id)
                
                steps = result.get("steps", [])
                ticket_subject = result.get("ticket_subject", "N/A")
                total_steps = result.get("total_steps", 0)
                articles_used = result.get("articles_used", 0)
                
                # Format the response
                response_text = f"📋 Suggested Next Steps for Ticket #{ticket_id}\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Ticket Subject: {ticket_subject}\n"
                response_text += f"Based on {articles_used} knowledge base article(s)\n\n"
                
                if steps and len(steps) > 0:
                    for idx, step in enumerate(steps, 1):
                        title = step.get('title', 'Untitled Step')
                        description = step.get('description', 'No description available')
                        source = step.get('source_article', 'Unknown')
                        source_id = step.get('source_article_id', None)
                        
                        response_text += f"{idx}. {title}\n"
                        response_text += f"   Description: {description}\n"
                        if source != 'System Generated':
                            if source_id:
                                response_text += f"   Source: {source} (ID: {source_id})\n"
                            else:
                                response_text += f"   Source: {source}\n"
                        response_text += "\n"
                else:
                    response_text += "No suggested steps found. Please review the ticket manually.\n"
                
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": response_text}]
                }
            except PermissionError as e:
                logger.error(f"Permission error getting suggested next steps: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"I'm unable to access ticket #{ticket_id} due to permission restrictions. "
                                                         f"The ticket exists but your current access level doesn't allow viewing it.\n\n"
                                                         f"The consistent **403 Forbidden error** indicates this is a **permissions issue** "
                                                         f"that won't resolve by retrying.\n\n"
                                                         f"**To move forward, you have a few options:**\n\n"
                                                         f"1. **Contact your administrator** to grant you access to ticket #{ticket_id}\n"
                                                         f"2. **Verify the ticket number** - perhaps you meant a different ticket ID?\n"
                                                         f"3. **Check a ticket you do have access to** - try a different ticket ID\n"
                                                         f"4. **List available tickets** to see which ones you can access\n\n"
                                                         f"Would you like me to help with any of these alternatives?"}]
                }
            except ValueError as e:
                logger.error(f"Value error getting suggested next steps: {e}")
                error_msg = str(e)
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"❌ {error_msg}\n\nPlease verify that ticket ID {ticket_id} exists."}]
                }
            except Exception as e:
                logger.error(f"Error getting suggested next steps: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Error getting suggested next steps: {str(e)}"}]
                }
        
        elif tool_request.name == "get_ticket_comments":
            ticket_id = tool_request.arguments.get("ticket_id")
            if not ticket_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a ticket ID"}]
                }
            try:
                comments_result = fetch_ticket_comments(ticket_id)
                
                # Handle different response formats
                if isinstance(comments_result, dict):
                    comments = comments_result.get("comments", comments_result.get("data", []))
                    total = comments_result.get("total", len(comments))
                elif isinstance(comments_result, list):
                    comments = comments_result
                    total = len(comments)
                else:
                    comments = []
                    total = 0
                
                # Format the response
                response_text = f"💬 Comments for Ticket #{ticket_id}\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Total Comments: {total}\n\n"
                
                if comments and len(comments) > 0:
                    for idx, comment in enumerate(comments, 1):
                        comment_text = comment.get('comment', comment.get('content', comment.get('text', 'No content')))
                        author = comment.get('authorName', comment.get('author', comment.get('createdBy', 'Unknown')))
                        created_at = comment.get('createdAt', comment.get('timestamp', comment.get('date', 'N/A')))
                        comment_id = comment.get('id', 'N/A')
                        is_internal = comment.get('isInternal', comment.get('internal', False))
                        
                        response_text += f"{idx}. Comment #{comment_id}\n"
                        response_text += f"   {'─' * 50}\n"
                        response_text += f"   Author: {author}\n"
                        response_text += f"   Date: {created_at}\n"
                        response_text += f"   isInternal: {is_internal}\n"
                        response_text += f"   Content:\n"
                        # Clean and format comment text
                        comment_lines = str(comment_text).split('\n')
                        for line in comment_lines:
                            if line.strip():
                                response_text += f"   {line.strip()}\n"
                        response_text += "\n"
                else:
                    response_text += "No comments found for this ticket.\n"
                
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": response_text}]
                }
            except PermissionError as e:
                logger.error(f"Permission error getting ticket comments: {e}")
                error_msg = str(e)
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"❌ {error_msg}\n\nCould you verify that ticket ID {ticket_id} is correct and that you have the necessary permissions to access its comments?"}]
                }
            except ValueError as e:
                logger.error(f"Value error getting ticket comments: {e}")
                error_msg = str(e)
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"❌ {error_msg}\n\nPlease verify that ticket ID {ticket_id} exists."}]
                }
            except Exception as e:
                logger.error(f"Error getting ticket comments: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Error getting ticket comments: {str(e)}"}]
                }
        
        elif tool_request.name == "get_suggested_response":
            ticket_id = tool_request.arguments.get("ticket_id")
            if not ticket_id:
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": "Please provide a ticket ID"}]
                }
            try:
                result = generate_suggested_response(ticket_id)
                
                suggested_response = result.get("suggested_response", "")
                ticket_subject = result.get("ticket_subject", "N/A")
                customer_name = result.get("customer_name", "Customer")
                steps_used = result.get("steps_used", 0)
                articles_used = result.get("articles_used", 0)
                comments_analyzed = result.get("comments_analyzed", 0)
                sentiment = result.get("sentiment", "neutral")
                sentiment_score = result.get("sentiment_score", 0)
                sentiment_indicators = result.get("sentiment_indicators", [])
                
                # Format sentiment display
                sentiment_display = {
                    'very_negative': '🔴 Very Negative',
                    'negative': '🟠 Negative',
                    'neutral': '🟡 Neutral',
                    'positive': '🟢 Positive'
                }.get(sentiment, sentiment.title())
                
                # Format the response
                response_text = f"📝 Suggested Response for Ticket #{ticket_id}\n"
                response_text += f"{'=' * 50}\n\n"
                response_text += f"Ticket: {ticket_subject}\n"
                response_text += f"Customer: {customer_name}\n"
                response_text += f"Sentiment: {sentiment_display} (Score: {sentiment_score})\n"
                if sentiment_indicators:
                    response_text += f"Indicators: {', '.join(sentiment_indicators)}\n"
                response_text += f"Based on: {articles_used} article(s), {comments_analyzed} comment(s)\n\n"
                response_text += f"{'─' * 50}\n"
                response_text += f"SUGGESTED RESPONSE:\n"
                response_text += f"{'─' * 50}\n\n"
                response_text += suggested_response
                
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": response_text}]
                }
            except PermissionError as e:
                logger.error(f"Permission error generating suggested response: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"I'm unable to access ticket #{ticket_id} due to permission restrictions. "
                                                         f"The ticket exists but your current access level doesn't allow viewing it.\n\n"
                                                         f"The consistent **403 Forbidden error** indicates this is a **permissions issue** "
                                                         f"that won't resolve by retrying.\n\n"
                                                         f"**To move forward, you have a few options:**\n\n"
                                                         f"1. **Contact your administrator** to grant you access to ticket #{ticket_id}\n"
                                                         f"2. **Verify the ticket number** - perhaps you meant a different ticket ID?\n"
                                                         f"3. **Check a ticket you do have access to** - try a different ticket ID\n"
                                                         f"4. **List available tickets** to see which ones you can access\n\n"
                                                         f"Would you like me to help with any of these alternatives?"}]
                }
            except ValueError as e:
                logger.error(f"Value error generating suggested response: {e}")
                error_msg = str(e)
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"❌ {error_msg}\n\nPlease verify that ticket ID {ticket_id} exists."}]
                }
            except Exception as e:
                logger.error(f"Error generating suggested response: {e}")
                return {
                    "tool": tool_request.name,
                    "content": [{"type": "text", "text": f"Error generating suggested response: {str(e)}"}]
                }
        
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_request.name}")
            
    except Exception as e:
        logger.error(f"Error calling tool {tool_request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/resources")
async def list_resources(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """List available MCP resources."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Return hardcoded resources list (matching MCP server resources)
        return {
            "resources": [
                {
                    "uri": "servicenex://articles/all",
                    "name": "All Knowledge Base Articles",
                    "description": "Complete list of published knowledge base articles",
                    "mimeType": "application/json"
                },
                {
                    "uri": "servicenex://tickets/recent",
                    "name": "Recent Support Tickets",
                    "description": "List of recent support tickets",
                    "mimeType": "application/json"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/resources/read")
async def read_resource(
    resource_request: ResourceReadRequest,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Read an MCP resource."""
    try:
        # Set API key from header if provided
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Route to appropriate data loader based on URI
        if resource_request.uri == "servicenex://articles/all":
            result = fetch_articles(category="all", page=1, limit=100)
            content = json.dumps(result, indent=2)
        
        elif resource_request.uri == "servicenex://tickets/recent":
            result = fetch_tickets(category="all", page=1, limit=50)
            content = json.dumps(result, indent=2)
        
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown resource URI: {resource_request.uri}"
            )
        
        return {
            "uri": resource_request.uri,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading resource {resource_request.uri}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience endpoints for specific tools
@app.get("/api/tickets")
async def get_tickets_api(
    request: Request,
    limit: int = 5,
    page: int = 1,
    category: str = "all",
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Get tickets - REST API endpoint."""
    try:
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Call the data loader directly
        result = fetch_tickets(category=category, page=page, limit=limit)
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles")
async def get_articles_api(
    request: Request,
    limit: int = 10,
    page: int = 1,
    category: str = "all",
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Get articles - REST API endpoint."""
    try:
        api_key = get_api_key_from_header(request) or x_api_key
        if api_key:
            os.environ["MY_API_KEY"] = api_key
        
        # Call the data loader directly
        result = fetch_articles(category=category, page=page, limit=limit)
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

