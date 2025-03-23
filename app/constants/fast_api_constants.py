
class FastAPIConstants:
    TITLE = "Enterprise | Server"
    DESCRIPTION = """
### Project Description: Enterprise 

#### Overview
**Enterprise** is a server-side backend project for billing and stock management.

#### Key Features
- **Billing:**  Create a new order, view order history, and manage customer details.
- **Stock Management:** Add new products, update stock, and manage product details.

#### Technology Stack
- **Programming Language:** Python
- **Framework:** FastAPI

#### Team Members
- **Developer:** Khursheed, Nooman
- **Manager:** Nooman

This project leverages the capabilities of FastAPI to ensure a high-performance, scalable, and robust backend infrastructure, supporting the AI-driven features that make document management and interaction more intuitive and powerful.
    """
    SUMMARY = "Project Summary"
    VERSION = "1.0.0"
    T_N_C = "http://erp.com/terms-and-conditions"
    CONTACT = {
        "name": "Nooman Khan",
        "url": "https://erp.com",
        "email": "khannooman8586@gmail.com",
    }
    LICENSE_INFO = {
        "name": "ERP",
        "url": "http://erp/license",
    }

    OPENAPI_TAGS_METADATA = [
        {
            "name": "API Testings",
            "description": "Provides a route to run tests at deployment time."
        },
        {
            "name": "Health",
            "description": "Check health of the server"
        },
        {
            "name": "Chat",
            "description": "Conversational chatbot with RAG"
        },
    ]
