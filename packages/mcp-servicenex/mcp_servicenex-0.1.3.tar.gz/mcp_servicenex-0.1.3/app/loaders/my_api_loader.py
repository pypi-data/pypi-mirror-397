import requests
import re
from html.parser import HTMLParser
from app.config import MY_API_BASE_URL, MY_API_KEY

def fetch_tickets(category="all", page=1, limit=10):
    """
    Fetch support tickets from the ServiceNex API with pagination support
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json"
    }
    
    params = {
        "category": category,
        "page": page,
        "limit": limit
    }
    
    url = f"{MY_API_BASE_URL}/tickets"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def fetch_articles(category="all", page=1, limit=10):
    """
    Fetch articles from the knowledge base API with pagination and filtering
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json"
    }
    
    params = {
        "category": category,
        "page": page,
        "limit": limit
    }
    
    url = f"{MY_API_BASE_URL}/knowledge/published"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def fetch_ticket_by_id(ticket_id):
    """
    Fetch a specific ticket by ID from the ServiceNex API
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{MY_API_BASE_URL}/tickets/{ticket_id}"
    response = requests.get(url, headers=headers)
    
    # Handle HTTP errors with user-friendly messages
    if response.status_code == 403:
        # Try to get more details from the response
        error_details = ""
        try:
            error_response = response.json()
            if isinstance(error_response, dict):
                error_message = error_response.get('message', error_response.get('error', ''))
                if error_message:
                    error_details = f"\n\nAPI Response: {error_message}"
        except:
            pass
        
        raise PermissionError(
            f"403 Forbidden: Access denied to ticket {ticket_id}.\n\n"
            "The ticket exists in the system, but your API key does not have permission to access it.\n\n"
            "Possible reasons:\n"
            "1. **Role-based access control** - Your API key's role may not have access to this ticket\n"
            "2. **Organization/tenant restriction** - The ticket may belong to a different organization\n"
            "3. **Ticket ownership** - You may only have access to tickets assigned to you or your team\n"
            "4. **API key scope** - Your API key may have limited permissions for ticket access\n\n"
            "To resolve this:\n"
            "- Verify that your API key has the necessary permissions/roles\n"
            "- Check if the ticket belongs to your organization/tenant\n"
            "- Contact your administrator to grant access to this ticket\n"
            f"{error_details}"
        )
    elif response.status_code == 404:
        raise ValueError(f"404 Not Found: Ticket {ticket_id} does not exist.")
    elif response.status_code == 401:
        raise PermissionError(
            "401 Unauthorized: Invalid API key. Please check your MY_API_KEY configuration."
        )
    elif not response.ok:
        response.raise_for_status()
    
    return response.json()

def fetch_ticket_comments(ticket_id):
    """
    Fetch all comments for a specific ticket ID from the ServiceNex API
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    url = f"{MY_API_BASE_URL}/tickets/{ticket_id}/all-comments"
    response = requests.get(url, headers=headers)
    
    # Handle HTTP errors with user-friendly messages
    if response.status_code == 403:
        # Try to get more details from the response
        error_details = ""
        try:
            error_response = response.json()
            if isinstance(error_response, dict):
                error_message = error_response.get('message', error_response.get('error', ''))
                if error_message:
                    error_details = f"\n\nAPI Response: {error_message}"
        except:
            pass
        
        raise PermissionError(
            f"403 Forbidden: Access denied to comments for ticket {ticket_id}.\n\n"
            "The ticket exists in the system, but your API key does not have permission to access its comments.\n\n"
            "Possible reasons:\n"
            "1. **Role-based access control** - Your API key's role may not have access to ticket comments\n"
            "2. **Organization/tenant restriction** - The ticket may belong to a different organization\n"
            "3. **API key scope** - Your API key may have limited permissions for comment access\n\n"
            "To resolve this:\n"
            "- Verify that your API key has the necessary permissions/roles\n"
            "- Check if the ticket belongs to your organization/tenant\n"
            "- Contact your administrator to grant access to ticket comments\n"
            f"{error_details}"
        )
    elif response.status_code == 404:
        raise ValueError(f"404 Not Found: Ticket {ticket_id} does not exist.")
    elif response.status_code == 401:
        raise PermissionError(
            "401 Unauthorized: Invalid API key. Please check your MY_API_KEY configuration."
        )
    elif not response.ok:
        response.raise_for_status()
    
    return response.json()

def fetch_articles_by_ticket_id(ticket_id):
    """
    Fetch knowledge base articles related to a specific ticket ID.
    First fetches the ticket by ID, then searches articles based on:
    - Ticket title (subject)
    - Ticket description
    - Ticket category
    
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    # Step 1: Fetch the ticket by ID
    try:
        ticket = fetch_ticket_by_id(ticket_id)
    except (PermissionError, ValueError) as e:
        # Re-raise with context
        raise
    except Exception as e:
        raise Exception(f"Error fetching ticket {ticket_id}: {str(e)}")
    
    if not ticket:
        return {"articles": [], "total": 0, "ticket_id": ticket_id}
    
    # Step 2: Extract search criteria from ticket
    ticket_subject = ticket.get('subject', '').lower()
    ticket_description = ticket.get('description', '').lower()
    ticket_category = ticket.get('categoryName', ticket.get('category', ''))
    ticket_type = ticket.get('typeName', ticket.get('type', ''))
    
    # Common stop words to filter out (not meaningful for matching)
    stop_words = {
        'test', 'tests', 'testing', 'the', 'this', 'that', 'these', 'those',
        'with', 'from', 'into', 'have', 'has', 'had', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'cannot',
        'about', 'after', 'before', 'during', 'through', 'under', 'over',
        'above', 'below', 'between', 'among', 'within', 'without', 'against',
        'approval', 'approve', 'approved', 'cab', 'request', 'requests'
    }
    
    # Extract meaningful keywords from subject and description (filter stop words)
    subject_words = set(
        word for word in ticket_subject.split() 
        if len(word) > 3 and word not in stop_words
    )
    description_words = set(
        word for word in ticket_description.split() 
        if len(word) > 3 and word not in stop_words
    )
    search_keywords = subject_words.union(description_words)
    
    # If we have no meaningful keywords and no category, return empty results
    # (tickets with only generic words like "test", "approval" won't match anything)
    if not search_keywords and not ticket_category:
        return {
            "articles": [],
            "total": 0,
            "ticket_id": ticket_id,
            "ticket_subject": ticket.get('subject', ''),
            "search_criteria": {
                "category": ticket_category,
                "keywords": []
            }
        }
    
    # Step 3: Fetch articles (fetch more for better matching)
    articles_result = fetch_articles(category="all", page=1, limit=100)
    
    # Step 4: Filter articles based on ticket information
    if isinstance(articles_result, dict) and "articles" in articles_result:
        all_articles = articles_result["articles"]
    elif isinstance(articles_result, list):
        all_articles = articles_result
    else:
        all_articles = []
    
    matched_articles = []
    
    for article in all_articles:
        article_title = article.get('title', '').lower()
        article_category = article.get('categoryName', article.get('category', ''))
        article_content = article.get('content', '').lower()
        
        score = 0
        match_reasons = []
        
        # Category match (highest priority)
        if ticket_category and article_category:
            if ticket_category.lower() == article_category.lower():
                score += 10
                match_reasons.append("category_match")
        
        # Type match
        if ticket_type and article_category:
            if ticket_type.lower() in article_category.lower() or article_category.lower() in ticket_type.lower():
                score += 5
                match_reasons.append("type_match")
        
        # Title keyword matches
        title_matches = sum(1 for keyword in search_keywords if keyword in article_title)
        if title_matches > 0:
            score += title_matches * 3
            match_reasons.append(f"title_keywords({title_matches})")
        
        # Description keyword matches in article title
        desc_in_title = sum(1 for keyword in description_words if keyword in article_title)
        if desc_in_title > 0:
            score += desc_in_title * 2
            match_reasons.append(f"desc_in_title({desc_in_title})")
        
        # Description keyword matches in article content (lower weight, only if we have meaningful keywords)
        if article_content and len(search_keywords) > 0:
            content_matches = sum(1 for keyword in search_keywords if keyword in article_content)
            # Only count if we have multiple matches (more reliable)
            if content_matches >= 2:
                score += content_matches
                match_reasons.append(f"content_keywords({content_matches})")
        
        # Subject match in title (exact or partial) - only meaningful words
        if ticket_subject and len(search_keywords) > 0:
            subject_words_in_title = [w for w in search_keywords if w in article_title]
            if subject_words_in_title:
                score += len(subject_words_in_title) * 4
                match_reasons.append(f"subject_in_title({len(subject_words_in_title)})")
        
        # Minimum score threshold: Require at least 5 points OR a category match
        # This ensures we only return articles with meaningful relevance
        min_score_threshold = 5
        has_category_match = "category_match" in match_reasons
        
        if score >= min_score_threshold or has_category_match:
            article['_match_score'] = score
            article['_match_reasons'] = match_reasons
            matched_articles.append(article)
    
    # Sort by match score (highest first)
    matched_articles.sort(key=lambda x: x.get('_match_score', 0), reverse=True)
    
    return {
        "articles": matched_articles,
        "total": len(matched_articles),
        "ticket_id": ticket_id,
        "ticket_subject": ticket.get('subject', ''),
        "search_criteria": {
            "category": ticket_category,
            "keywords": list(search_keywords)[:10]  # Limit to first 10 keywords
        }
    }

def extract_next_steps_from_articles(articles):
    """
    Extract suggested next steps from knowledge base articles.
    Parses HTML content to find numbered steps, troubleshooting procedures, and action items.
    
    Args:
        articles: List of article dictionaries with 'content' field
        
    Returns:
        List of step dictionaries with 'title' and 'description'
    """
    steps = []
    seen_steps = set()  # To avoid duplicates
    
    for article in articles:
        content = article.get('content', '')
        if not content:
            continue
        
        # Parse HTML to extract structured content
        # Look for ordered lists (<ol>), numbered headings, and step sections
        
        # Pattern 1: Extract from ordered lists (<ol><li>...</li></ol>)
        ol_pattern = r'<ol[^>]*>(.*?)</ol>'
        ol_matches = re.findall(ol_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for ol_content in ol_matches:
            # Extract list items
            li_pattern = r'<li[^>]*>(.*?)</li>'
            li_matches = re.findall(li_pattern, ol_content, re.DOTALL | re.IGNORECASE)
            
            for idx, li_text in enumerate(li_matches, 1):
                # Clean HTML tags
                clean_text = re.sub(r'<[^>]+>', '', li_text)
                clean_text = clean_text.replace('&nbsp;', ' ').replace('&amp;', '&')
                clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>')
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                if len(clean_text) > 20:  # Only include substantial steps
                    # Try to extract title and description
                    if ':' in clean_text:
                        parts = clean_text.split(':', 1)
                        title = parts[0].strip()
                        description = parts[1].strip()
                    else:
                        title = clean_text[:100] if len(clean_text) > 100 else clean_text
                        description = clean_text
                    
                    step_key = title.lower()[:50]  # Use first 50 chars as key
                    if step_key not in seen_steps:
                        seen_steps.add(step_key)
                        steps.append({
                            'title': title,
                            'description': description,
                            'source_article': article.get('title', 'Unknown'),
                            'source_article_id': article.get('id', None)
                        })
        
        # Pattern 2: Extract from headings with numbers (h2, h3 with step numbers)
        heading_pattern = r'<h[23][^>]*>.*?(\d+)[\.\)]\s*(.*?)</h[23]>'
        heading_matches = re.findall(heading_pattern, content, re.IGNORECASE)
        
        for num, heading_text in heading_matches:
            clean_heading = re.sub(r'<[^>]+>', '', heading_text).strip()
            if clean_heading and len(clean_heading) > 10:
                # Try to find the description after the heading
                heading_full_pattern = rf'<h[23][^>]*>.*?{re.escape(num)}[\.\)]\s*{re.escape(clean_heading)}</h[23]>(.*?)(?=<h[23]|<ol|</p>|$)'
                desc_match = re.search(heading_full_pattern, content, re.DOTALL | re.IGNORECASE)
                
                description = ""
                if desc_match:
                    desc_text = desc_match.group(1)
                    desc_text = re.sub(r'<[^>]+>', '', desc_text)
                    desc_text = desc_text.replace('&nbsp;', ' ').strip()
                    description = desc_text[:500]  # Limit description length
                
                step_key = clean_heading.lower()[:50]
                if step_key not in seen_steps:
                    seen_steps.add(step_key)
                    steps.append({
                        'title': clean_heading,
                        'description': description if description else clean_heading,
                        'source_article': article.get('title', 'Unknown'),
                        'source_article_id': article.get('id', None)
                    })
        
        # Pattern 3: Extract from paragraphs with step indicators
        step_pattern = r'(?:Step\s+\d+|^\d+[\.\)])\s*[:\-]?\s*(.+?)(?=\n|$|Step\s+\d+|\d+[\.\)])'
        step_matches = re.findall(step_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for step_text in step_matches:
            clean_step = re.sub(r'<[^>]+>', '', step_text)
            clean_step = clean_step.replace('&nbsp;', ' ').strip()
            
            if len(clean_step) > 20:
                if ':' in clean_step:
                    parts = clean_step.split(':', 1)
                    title = parts[0].strip()
                    description = parts[1].strip()
                else:
                    title = clean_step[:100] if len(clean_step) > 100 else clean_step
                    description = clean_step
                
                step_key = title.lower()[:50]
                if step_key not in seen_steps:
                    seen_steps.add(step_key)
                    steps.append({
                        'title': title,
                        'description': description,
                        'source_article': article.get('title', 'Unknown'),
                        'source_article_id': article.get('id', None)
                    })
    
    # Limit to top 10 most relevant steps
    return steps[:10]

def analyze_sentiment(ticket_description, comments):
    """
    Analyze sentiment from ticket description and customer comments.
    
    Args:
        ticket_description: The ticket description text
        comments: List of comment dictionaries
        
    Returns:
        Dictionary with sentiment analysis results:
        - sentiment: 'positive', 'neutral', 'negative', 'very_negative'
        - score: Sentiment score (-1 to 1, where -1 is very negative, 1 is very positive)
        - indicators: List of sentiment indicators found
    """
    # Negative sentiment indicators
    negative_words = [
        'frustrated', 'frustrating', 'frustration', 'angry', 'angry', 'annoyed', 'annoying',
        'disappointed', 'disappointing', 'upset', 'unhappy', 'terrible', 'awful', 'horrible',
        'worst', 'bad', 'poor', 'slow', 'broken', 'not working', "doesn't work", "won't work",
        'failed', 'failure', 'error', 'errors', 'issue', 'issues', 'problem', 'problems',
        'unacceptable', 'unacceptable', 'ridiculous', 'pathetic', 'useless', 'waste',
        'complaint', 'complain', 'refund', 'cancel', 'cancellation', 'dissatisfied',
        'unreliable', 'unstable', 'crash', 'crashed', 'down', 'outage', 'outages'
    ]
    
    # Very negative/angry indicators
    very_negative_words = [
        'extremely', 'very', 'completely', 'totally', 'absolutely', 'ridiculous',
        'unacceptable', 'outrageous', 'infuriating', 'disgusted', 'disgusting',
        'furious', 'livid', 'enraged', 'demand', 'demanding', 'immediately', 'now',
        'asap', 'as soon as possible', 'escalate', 'escalation', 'manager', 'supervisor'
    ]
    
    # Positive sentiment indicators
    positive_words = [
        'thank', 'thanks', 'appreciate', 'appreciated', 'helpful', 'great', 'good',
        'excellent', 'wonderful', 'pleased', 'satisfied', 'happy', 'glad', 'perfect',
        'working', 'fixed', 'resolved', 'solution', 'solved'
    ]
    
    # Urgency indicators
    urgency_words = [
        'urgent', 'urgently', 'asap', 'as soon as possible', 'immediately', 'critical',
        'emergency', 'blocking', 'blocked', 'cannot', "can't", 'unable', 'stuck'
    ]
    
    # Combine all text for analysis
    all_text = (ticket_description or '').lower()
    
    # Add customer comments (exclude internal comments)
    customer_comments_text = []
    for comment in comments:
        is_internal = comment.get('isInternal', comment.get('internal', False))
        if not is_internal:
            comment_text = comment.get('comment', comment.get('content', comment.get('text', '')))
            if comment_text:
                customer_comments_text.append(str(comment_text).lower())
    
    all_text += ' ' + ' '.join(customer_comments_text)
    
    # Count sentiment indicators
    negative_count = sum(1 for word in negative_words if word in all_text)
    very_negative_count = sum(1 for word in very_negative_words if word in all_text)
    positive_count = sum(1 for word in positive_words if word in all_text)
    urgency_count = sum(1 for word in urgency_words if word in all_text)
    
    # Calculate sentiment score
    score = 0
    score -= negative_count * 0.3
    score -= very_negative_count * 0.5
    score += positive_count * 0.2
    score -= urgency_count * 0.2  # Urgency often indicates frustration
    
    # Determine sentiment category
    if score <= -0.8 or very_negative_count >= 3:
        sentiment = 'very_negative'
    elif score <= -0.3 or negative_count >= 3:
        sentiment = 'negative'
    elif score >= 0.3 or positive_count >= 2:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'
    
    # Collect indicators
    indicators = []
    if negative_count > 0:
        indicators.append(f"{negative_count} negative indicator(s)")
    if very_negative_count > 0:
        indicators.append(f"{very_negative_count} very negative indicator(s)")
    if positive_count > 0:
        indicators.append(f"{positive_count} positive indicator(s)")
    if urgency_count > 0:
        indicators.append(f"{urgency_count} urgency indicator(s)")
    
    return {
        'sentiment': sentiment,
        'score': round(score, 2),
        'indicators': indicators,
        'negative_count': negative_count,
        'very_negative_count': very_negative_count,
        'positive_count': positive_count,
        'urgency_count': urgency_count
    }

def get_suggested_next_steps(ticket_id):
    """
    Get suggested next steps for a ticket based on related knowledge base articles.
    
    Args:
        ticket_id: The ticket ID to get steps for
        
    Returns:
        Dictionary with 'steps' list and ticket information
        
    Raises:
        PermissionError: If access to the ticket is denied (403)
        ValueError: If the ticket doesn't exist (404)
        Exception: For other errors
    """
    # Get related articles
    try:
        articles_result = fetch_articles_by_ticket_id(ticket_id)
    except (PermissionError, ValueError) as e:
        # Re-raise permission and not found errors as-is
        raise
    except Exception as e:
        raise Exception(f"Error getting suggested next steps for ticket {ticket_id}: {str(e)}")
    
    if isinstance(articles_result, dict):
        articles = articles_result.get("articles", [])
        ticket_subject = articles_result.get("ticket_subject", "N/A")
    else:
        articles = []
        ticket_subject = "N/A"
    
    # Extract steps from articles (prioritize top 3 most relevant articles)
    top_articles = articles[:3] if len(articles) > 3 else articles
    steps = extract_next_steps_from_articles(top_articles)
    
    # If no steps found, create generic steps based on ticket info
    if not steps:
        steps = [
            {
                'title': 'Review ticket details',
                'description': f'Review the ticket subject "{ticket_subject}" and description to understand the issue.',
                'source_article': 'System Generated'
            },
            {
                'title': 'Check related knowledge base articles',
                'description': 'Search the knowledge base for articles related to this issue type.',
                'source_article': 'System Generated'
            },
            {
                'title': 'Escalate if needed',
                'description': 'If the issue cannot be resolved with available resources, escalate to the appropriate team.',
                'source_article': 'System Generated'
            }
        ]
    
    return {
        'ticket_id': ticket_id,
        'ticket_subject': ticket_subject,
        'steps': steps,
        'total_steps': len(steps),
        'articles_used': len(top_articles)
    }

def generate_suggested_response(ticket_id):
    """
    Generate a suggested response for a ticket by analyzing:
    - Ticket details (subject, description, customer)
    - All comments on the ticket
    - Related knowledge base articles
    
    Args:
        ticket_id: The ticket ID to generate response for
        
    Returns:
        Dictionary with suggested response text and metadata
        
    Raises:
        PermissionError: If access to the ticket is denied (403)
        ValueError: If the ticket doesn't exist (404)
        Exception: For other errors
    """
    try:
        # Step 1: Fetch ticket details
        ticket = fetch_ticket_by_id(ticket_id)
        
        # Step 2: Fetch all comments
        try:
            comments_result = fetch_ticket_comments(ticket_id)
            if isinstance(comments_result, dict):
                comments = comments_result.get("comments", comments_result.get("data", []))
            elif isinstance(comments_result, list):
                comments = comments_result
            else:
                comments = []
        except Exception as e:
            # If comments can't be fetched, continue without them
            logger = __import__('logging').getLogger(__name__)
            logger.warning(f"Could not fetch comments for ticket {ticket_id}: {e}")
            comments = []
        
        # Step 3: Fetch related knowledge base articles
        try:
            articles_result = fetch_articles_by_ticket_id(ticket_id)
            if isinstance(articles_result, dict):
                articles = articles_result.get("articles", [])
            elif isinstance(articles_result, list):
                articles = articles_result
            else:
                articles = []
        except Exception as e:
            # If articles can't be fetched, continue without them
            logger = __import__('logging').getLogger(__name__)
            logger.warning(f"Could not fetch articles for ticket {ticket_id}: {e}")
            articles = []
        
        # Step 4: Extract information
        ticket_subject = ticket.get('subject', '')
        ticket_description = ticket.get('description', '')
        customer_name = ticket.get('customerName', 'Customer')
        # Try to get first name if full name is available
        if customer_name and customer_name != 'Customer':
            first_name = customer_name.split()[0] if ' ' in customer_name else customer_name
        else:
            first_name = 'Customer'
        
        # Step 5: Analyze sentiment
        sentiment_analysis = analyze_sentiment(ticket_description, comments)
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        sentiment_score = sentiment_analysis.get('score', 0)
        
        # Step 6: Extract actionable steps from articles
        top_articles = articles[:2] if len(articles) > 2 else articles  # Use top 2 articles
        steps = extract_next_steps_from_articles(top_articles)
        
        # Step 7: Build suggested response with sentiment-aware tone
        response_parts = []
        
        # Greeting - adjust based on sentiment
        if sentiment == 'very_negative':
            response_parts.append(f"Hello {first_name},")
            response_parts.append("We sincerely apologize for the frustration and inconvenience you've experienced.")
        elif sentiment == 'negative':
            response_parts.append(f"Hello {first_name},")
            response_parts.append("We apologize for the inconvenience and appreciate you bringing this to our attention.")
        else:
            response_parts.append(f"Hello {first_name}, thank you for reaching out.")
        
        # Check if urgent based on ticket priority or comments
        priority = ticket.get('priority', '').lower()
        is_urgent = priority in ['high', 'urgent', 'critical'] or any(
            'urgent' in str(comment.get('comment', '')).lower() 
            for comment in comments
        )
        
        # Urgency acknowledgment - adjust based on sentiment
        if is_urgent:
            if sentiment in ['very_negative', 'negative']:
                response_parts.append("We understand this is urgent and are prioritizing your case immediately.")
            else:
                response_parts.append("We understand this is urgent.")
        
        # Main body with steps
        if steps and len(steps) > 0:
            response_parts.append("Here's what we suggest as the next steps:")
            response_parts.append("")
            
            for idx, step in enumerate(steps[:5], 1):  # Limit to top 5 steps
                title = step.get('title', '')
                description = step.get('description', '')
                
                # Format step title
                if title:
                    response_parts.append(f"{idx}. **{title}**")
                else:
                    response_parts.append(f"{idx}. {description[:100]}")
                
                # Add description if it's different from title
                if description and description != title:
                    # Try to extract bullet points or sub-steps
                    desc_lines = description.split('\n')
                    for line in desc_lines:
                        line = line.strip()
                        if line:
                            # Check if it's a bullet point
                            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                                response_parts.append(f"   {line}")
                            elif any(marker in line.lower() for marker in ['step', 'close', 'navigate', 'restart', 'check', 'ensure', 'verify']):
                                response_parts.append(f"   • {line}")
                            else:
                                response_parts.append(f"   {line}")
                    response_parts.append("")
        else:
            # Generic response if no steps found
            response_parts.append("We're looking into this issue and will get back to you shortly.")
            if ticket_description:
                response_parts.append("")
                response_parts.append("Based on your description, we'll investigate and provide a solution.")
        
        # Closing - adjust based on sentiment
        response_parts.append("")
        if sentiment == 'very_negative':
            if steps and len(steps) > 0:
                response_parts.append("If the issue persists after trying these steps, please let us know immediately, and we will escalate this to our senior technical team for immediate resolution. We are committed to resolving this for you.")
            else:
                response_parts.append("We are escalating this to our senior technical team for immediate attention and will provide you with an update within the next few hours.")
            response_parts.append("We truly appreciate your patience and apologize again for the trouble this has caused.")
        elif sentiment == 'negative':
            if steps and len(steps) > 0:
                response_parts.append("If the issue persists, please let us know, and we will initiate further diagnostic checks. We'll work to resolve this as quickly as possible.")
            else:
                response_parts.append("We're actively working on this and will provide you with an update soon.")
            response_parts.append("Thank you for your patience, and we apologize for any inconvenience.")
        else:
            if steps and len(steps) > 0:
                response_parts.append("If the issue persists, let us know, and we will initiate further diagnostic checks. We'll work to resolve this as soon as possible.")
            else:
                response_parts.append("We'll work to resolve this as soon as possible.")
            response_parts.append("Thank you for your patience.")
        
        # Combine all parts
        suggested_response = "\n".join(response_parts)
        
        return {
            'ticket_id': ticket_id,
            'ticket_subject': ticket_subject,
            'customer_name': customer_name,
            'suggested_response': suggested_response,
            'steps_used': len(steps),
            'articles_used': len(top_articles),
            'comments_analyzed': len(comments),
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'sentiment_indicators': sentiment_analysis.get('indicators', [])
        }
        
    except (PermissionError, ValueError) as e:
        # Re-raise permission and not found errors as-is
        raise
    except Exception as e:
        raise Exception(f"Error generating suggested response for ticket {ticket_id}: {str(e)}")

# Keep fetch_data as an alias for backward compatibility
def fetch_data(category="all", page=1, limit=10):
    """Deprecated: Use fetch_tickets() instead"""
    return fetch_tickets(category=category, page=page, limit=limit)
