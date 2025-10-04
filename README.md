# Wegoit - Tour Reservation Management

Wegoit is a web application developed with Django to efficiently manage tour reservations, schedules, agencies, and payments.

## About the Project

This project is designed to centralize and streamline the operations of a tour agency. It allows for the management of tour details, scheduling, and tracking of reservations and their corresponding payments, whether made directly by the customer or through an agency.

## Features

- **Tour Management:** Create, edit, and manage tour details, including base price, capacity, and description.
- **Schedule Management:** Assign specific dates, times, and capacities for each tour.
- **Reservation Management:** Record new reservations, associating them with a customer, a tour schedule, and the number of passengers (pax).
- **Payment Tracking:** Register payments made, distinguishing between payments from agencies and direct payments from customers. It automatically calculates pending balances.
- **Agency Management:** Maintain a record of associated travel agencies.

## Technologies Used

- **Backend:**
  - Python
  - Django
- **Frontend:**
  - HTML
  - CSS
  - JavaScript
- **Database:**
  - SQLite (by default with Django, but can be configured for others like PostgreSQL, MySQL, etc.)