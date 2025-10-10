# Supplier Analysis Microservice

A microservice for analyzing supplier quality and reputation using Neo4j graph database.

## Overview

This microservice is designed to analyze supplier performance, quality, and reputation. It uses a Neo4j graph database to model complex relationships between suppliers, materials, complaints, and certificates. The microservice provides advanced analytics and generates detailed PDF reports about suppliers.

## Features

- Supplier quality and reputation analysis
- Complaint tracking and impact on supplier ratings
- Certificate management and tracking
- Recommendation of alternative suppliers
- Risk pattern detection for suppliers
- PDF report generation for supplier analysis
- Integration with Django through a REST API

## Graph Data Model

The Neo4j graph database includes these node types:

1. **Supplier**: Information about suppliers including contact info, materials, pricing, delivery time, and rating
2. **Material**: Information about materials that suppliers provide
3. **Complaint**: Issues filed against suppliers with severity tracking
4. **Certificate**: Supplier certifications with validity periods

And these relationships:

1. **SUPPLIES**: Connects suppliers to the materials they provide
2. **HAS_COMPLAINT**: Connects suppliers to complaints filed against them
3. **HAS_CERTIFICATE**: Connects suppliers to their certificates

## Setup and Installation

### Prerequisites

- Python 3.9+
- Neo4j 5.9+ database
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
