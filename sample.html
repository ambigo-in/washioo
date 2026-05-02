<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Car Wash Service Portal - Sample Flow</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .nav-tabs {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            background: #f5f5f5;
        }

        .nav-tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            background: #f5f5f5;
            border: none;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .nav-tab:hover {
            background: #eeeeee;
        }

        .nav-tab.active {
            background: #667eea;
            color: white;
            border-bottom: 3px solid #667eea;
        }

        .content {
            padding: 30px;
            display: none;
        }

        .content.active {
            display: block;
        }

        .section {
            margin-bottom: 30px;
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 22px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .section h3 {
            color: #333;
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }

        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            margin-right: 10px;
            margin-top: 10px;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }

        .btn-secondary:hover {
            background: #d0d0d0;
        }

        .btn-success {
            background: #4caf50;
            color: white;
        }

        .btn-success:hover {
            background: #45a049;
        }

        .btn-warning {
            background: #ff9800;
            color: white;
        }

        .btn-warning:hover {
            background: #e68900;
        }

        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }

        .alert.show {
            display: block;
        }

        .alert-info {
            background: #e3f2fd;
            color: #1565c0;
            border-left: 4px solid #1565c0;
        }

        .alert-success {
            background: #e8f5e9;
            color: #2e7d32;
            border-left: 4px solid #2e7d32;
        }

        .alert-warning {
            background: #fff3e0;
            color: #e65100;
            border-left: 4px solid #e65100;
        }

        .card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            background: #fafafa;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .card-title {
            font-weight: 600;
            color: #333;
        }

        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-pending {
            background: #fff3cd;
            color: #856404;
        }

        .badge-completed {
            background: #d4edda;
            color: #155724;
        }

        .badge-in-progress {
            background: #d1ecf1;
            color: #0c5460;
        }

        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .service-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }

        .service-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            transform: translateY(-5px);
        }

        .service-card.selected {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .service-card h4 {
            color: #333;
            margin-bottom: 10px;
        }

        .service-price {
            font-size: 24px;
            color: #667eea;
            font-weight: 700;
            margin: 10px 0;
        }

        .service-duration {
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
        }

        .address-list {
            display: grid;
            gap: 15px;
            margin-top: 20px;
        }

        .address-item {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .address-item:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .address-item.selected {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .address-label {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .address-text {
            font-size: 13px;
            color: #666;
        }

        .booking-summary {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }

        .booking-summary h3 {
            color: #667eea;
            margin-top: 0;
        }

        .summary-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            color: #333;
        }

        .summary-row strong {
            font-weight: 600;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .table th {
            background: #f0f4ff;
            color: #667eea;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e0e0e0;
        }

        .table td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }

        .table tr:hover {
            background: #fafafa;
        }

        .flow-diagram {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }

        .flow-step {
            display: inline-block;
            background: white;
            padding: 15px 25px;
            margin: 0 10px 10px 10px;
            border-radius: 5px;
            border: 2px solid #667eea;
            font-weight: 600;
            color: #667eea;
        }

        .flow-step:not(:last-child)::after {
            content: "→";
            margin-left: 20px;
            color: #667eea;
        }

        .code-block {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin-top: 10px;
        }

        .otp-input {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .otp-box {
            width: 50px;
            height: 50px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            border: 2px solid #ddd;
            border-radius: 5px;
        }

        .otp-box:focus {
            border-color: #667eea;
            outline: none;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-online {
            background: #4caf50;
        }

        .status-offline {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚗 Car Wash Service Portal</h1>
            <p>Complete Frontend Flow - HTML Sample</p>
        </div>

        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab(event, 'auth')">🔐 Authentication</button>
            <button class="nav-tab" onclick="showTab(event, 'services')">🛁 Services</button>
            <button class="nav-tab" onclick="showTab(event, 'booking')">📅 Booking</button>
            <button class="nav-tab" onclick="showTab(event, 'mybookings')">📋 My Bookings</button>
            <button class="nav-tab" onclick="showTab(event, 'admin')">👨‍💼 Admin</button>
            <button class="nav-tab" onclick="showTab(event, 'api')">📡 API Reference</button>
        </div>

        <!-- Content Sections -->
        <div class="content active" id="auth">
            <div class="section">
                <h2>🔐 Authentication Flow</h2>
                
                <div class="flow-diagram">
                    <span class="flow-step">Send OTP</span>
                    <span class="flow-step">Verify OTP</span>
                    <span class="flow-step">Signup/Signin</span>
                    <span class="flow-step">Get Tokens</span>
                </div>

                <div class="alert alert-info show">
                    <strong>Note:</strong> This flow supports multi-role registration. If user exists, they can add a new role!
                </div>

                <!-- Step 1: Send OTP -->
                <h3>Step 1: Send OTP</h3>
                <form onsubmit="sendOTP(event)">
                    <div class="form-group">
                        <label>Phone Number</label>
                        <input type="tel" id="phone" placeholder="+919876543210" required>
                        <small style="color: #666;">Response: Returns user_exist flag</small>
                    </div>
                    <button type="submit" class="btn btn-primary">Send OTP</button>
                </form>

                <div class="code-block">
POST /auth/send-otp
{
  "phone_number": "+919876543210"
}

Response:
{
  "message": "OTP sent successfully",
  "user_exist": true  // Important! Use this to determine flow
}</div>

                <!-- Step 2: Signup/Signin (Smart Flow) -->
                <h3>Step 2: Signup or Add Role</h3>
                <div class="alert alert-warning show">
                    <strong>Smart Flow:</strong> If user_exist is true, this becomes "Add Role". If false, it's "Signup"
                </div>

                <form onsubmit="signup(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" id="fullname" placeholder="John Doe">
                            <small style="color: #666;">Required for new users only</small>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="email" placeholder="john@example.com">
                            <small style="color: #666;">Required for new users only</small>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Role</label>
                            <select id="role" required>
                                <option value="">Select Role</option>
                                <option value="customer">Customer</option>
                                <option value="cleaner">Cleaner</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>OTP Code</label>
                            <input type="text" id="otp" placeholder="123456" required>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary">Signup / Add Role</button>
                </form>

                <div class="code-block">
POST /auth/signup
{
  "full_name": "John Doe",
  "phone_number": "+919876543210",
  "email": "john@example.com",
  "otp_code": "123456",
  "role": "customer"  // Can be customer or cleaner
}

Response (New User):
{
  "message": "User created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "is_new_user": true
}

Response (Adding Role):
{
  "message": "Role 'cleaner' added successfully to existing account",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "is_new_user": false  // Key difference!
}</div>

                <!-- Signin -->
                <h3>Step 3: Signin (Returning Users)</h3>
                <form onsubmit="signin(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Phone Number</label>
                            <input type="tel" placeholder="+919876543210" required>
                        </div>
                        <div class="form-group">
                            <label>OTP Code</label>
                            <input type="text" placeholder="123456" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Sign In</button>
                </form>

                <div class="code-block">
POST /auth/signin
{
  "phone_number": "+919876543210",
  "otp_code": "123456"
}

Response:
{
  "message": "Login successful",
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}</div>

                <!-- Token Management -->
                <h3>Step 4: Token Management</h3>
                <p><strong>Store tokens:</strong> access_token (short-lived) & refresh_token (long-lived)</p>

                <div class="code-block">
// Refresh Token (After access expires)
POST /auth/refresh-token
{
  "refresh_token": "..."
}

// Logout
POST /auth/logout
{
  "refresh_token": "..."
}</div>
            </div>
        </div>

        <!-- Services Tab -->
        <div class="content" id="services">
            <div class="section">
                <h2>🛁 Browse Services</h2>
                <p>Customers view available services and select one to book</p>

                <h3>Service Listing</h3>
                <div class="code-block">
GET /services/
Authorization: Bearer {access_token}

Response:
{
  "message": "Services fetched successfully",
  "services": [
    {
      "id": "uuid-1",
      "service_name": "Car Wash",
      "description": "Exterior and interior car wash service",
      "base_price": 499.00,
      "estimated_duration_minutes": 60,
      "is_active": true
    },
    {
      "id": "uuid-2",
      "service_name": "Bike Wash",
      "description": "Complete bike wash service",
      "base_price": 199.00,
      "estimated_duration_minutes": 30,
      "is_active": true
    }
  ],
  "total": 2
}</div>

                <h3>Services Grid</h3>
                <div class="service-grid">
                    <div class="service-card" onclick="selectService(this)">
                        <h4>🚗 Car Wash</h4>
                        <p style="color: #666; margin: 10px 0;">Full exterior & interior</p>
                        <div class="service-price">₹499</div>
                        <div class="service-duration">⏱️ 60 minutes</div>
                        <button class="btn btn-primary" style="width: 100%;">Select</button>
                    </div>

                    <div class="service-card" onclick="selectService(this)">
                        <h4>🏍️ Bike Wash</h4>
                        <p style="color: #666; margin: 10px 0;">Quick bike cleaning</p>
                        <div class="service-price">₹199</div>
                        <div class="service-duration">⏱️ 30 minutes</div>
                        <button class="btn btn-primary" style="width: 100%;">Select</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Booking Tab -->
        <div class="content" id="booking">
            <div class="section">
                <h2>📅 Book Service</h2>

                <div class="alert alert-info show">
                    <strong>Flow:</strong> Select Service → Manage Address → Schedule → Confirm
                </div>

                <!-- Step 1: Select Service -->
                <h3>Step 1: Selected Service</h3>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🚗 Car Wash</span>
                        <span style="color: #667eea; font-weight: 600;">₹499</span>
                    </div>
                    <div style="font-size: 13px; color: #666;">Full exterior & interior | 60 minutes</div>
                </div>

                <!-- Step 2: Address Management -->
                <h3>Step 2: Select / Create Address</h3>

                <button class="btn btn-secondary" onclick="toggleAddressForm()">+ Create New Address</button>

                <form id="addressForm" style="display: none; margin-top: 20px;" onsubmit="createAddress(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Label (Home/Office)</label>
                            <input type="text" placeholder="Home" required>
                        </div>
                        <div class="form-group">
                            <label>Address Line 1</label>
                            <input type="text" placeholder="123 Main Street" required>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>City</label>
                            <input type="text" placeholder="Bangalore" required>
                        </div>
                        <div class="form-group">
                            <label>Pincode</label>
                            <input type="text" placeholder="560001" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Landmark</label>
                        <input type="text" placeholder="Near XYZ Mall">
                    </div>

                    <button type="submit" class="btn btn-success">Create Address</button>
                    <button type="button" class="btn btn-secondary" onclick="toggleAddressForm()">Cancel</button>
                </form>

                <p style="margin: 20px 0; color: #666;"><strong>Saved Addresses:</strong></p>
                <div class="address-list">
                    <div class="address-item selected" onclick="selectAddress(this)">
                        <div class="address-label">🏠 Home</div>
                        <div class="address-text">123 Main Street, Bangalore 560001</div>
                        <div class="address-text">Near XYZ Mall</div>
                    </div>

                    <div class="address-item" onclick="selectAddress(this)">
                        <div class="address-label">🏢 Office</div>
                        <div class="address-text">456 Business Park, Bangalore 560034</div>
                    </div>
                </div>

                <div class="code-block">
GET /services/addresses
Authorization: Bearer {access_token}

POST /services/address
Authorization: Bearer {access_token}
{
  "address_label": "Home",
  "address_line1": "123 Main Street",
  "city": "Bangalore",
  "pincode": "560001",
  "landmark": "Near XYZ Mall"
}</div>

                <!-- Step 3: Schedule -->
                <h3>Step 3: Schedule Booking</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" required>
                    </div>
                    <div class="form-group">
                        <label>Time</label>
                        <input type="time" required>
                    </div>
                </div>

                <div class="form-group">
                    <label>Special Instructions</label>
                    <textarea placeholder="e.g., Ring bell twice, Gate password: 1234" rows="3"></textarea>
                </div>

                <!-- Booking Summary -->
                <div class="booking-summary">
                    <h3>Booking Summary</h3>
                    <div class="summary-row">
                        <span>Service:</span>
                        <strong>Car Wash</strong>
                    </div>
                    <div class="summary-row">
                        <span>Location:</span>
                        <strong>123 Main Street, Bangalore</strong>
                    </div>
                    <div class="summary-row">
                        <span>Date & Time:</span>
                        <strong>2024-05-15 @ 10:30 AM</strong>
                    </div>
                    <div class="summary-row">
                        <span>Estimated Price:</span>
                        <strong style="color: #667eea; font-size: 18px;">₹499</strong>
                    </div>
                </div>

                <button class="btn btn-success" style="width: 100%; padding: 15px; font-size: 16px;">Confirm Booking</button>

                <div class="code-block">
POST /services/book
Authorization: Bearer {access_token}
{
  "service_category_id": "uuid-1",
  "address_id": "uuid-address",
  "scheduled_date": "2024-05-15",
  "scheduled_time": "10:30:00",
  "special_instructions": "Ring bell twice"
}

Response:
{
  "message": "Booking created successfully",
  "booking": {
    "id": "uuid",
    "booking_reference": "BK-20240515-A1B2C3D4",
    "service_id": "uuid-1",
    "scheduled_date": "2024-05-15",
    "scheduled_time": "10:30:00",
    "booking_status": "pending",
    "estimated_price": 499,
    "created_at": "2024-05-10T10:30:00"
  }
}</div>
            </div>
        </div>

        <!-- My Bookings Tab -->
        <div class="content" id="mybookings">
            <div class="section">
                <h2>📋 My Bookings</h2>

                <div class="code-block">
GET /services/my-bookings
Authorization: Bearer {access_token}

Response:
{
  "message": "Bookings fetched successfully",
  "bookings": [...],
  "total": 3
}</div>

                <table class="table">
                    <thead>
                        <tr>
                            <th>Booking Ref</th>
                            <th>Service</th>
                            <th>Scheduled</th>
                            <th>Status</th>
                            <th>Price</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>BK-20240515-A1B2C3D4</strong></td>
                            <td>Car Wash</td>
                            <td>2024-05-15 @ 10:30 AM</td>
                            <td><span class="badge badge-in-progress">In Progress</span></td>
                            <td>₹499</td>
                            <td><button class="btn btn-secondary" style="font-size: 12px;">View</button></td>
                        </tr>
                        <tr>
                            <td><strong>BK-20240514-X9Y8Z7W6</strong></td>
                            <td>Bike Wash</td>
                            <td>2024-05-14 @ 3:00 PM</td>
                            <td><span class="badge badge-completed">Completed</span></td>
                            <td>₹199</td>
                            <td><button class="btn btn-secondary" style="font-size: 12px;">View</button></td>
                        </tr>
                        <tr>
                            <td><strong>BK-20240513-P5Q4R3S2</strong></td>
                            <td>Car Wash</td>
                            <td>2024-05-13 @ 11:00 AM</td>
                            <td><span class="badge badge-pending">Pending</span></td>
                            <td>₹499</td>
                            <td><button class="btn btn-secondary" style="font-size: 12px;">View</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Admin Tab -->
        <div class="content" id="admin">
            <div class="section">
                <h2>👨‍💼 Admin Dashboard</h2>

                <div class="alert alert-info show">
                    <strong>Admin Access:</strong> Only users with 'admin' role can access this section
                </div>

                <h3>View All Bookings</h3>
                <div class="code-block">
GET /services/admin/all-bookings
Authorization: Bearer {admin_access_token}

Response:
{
  "message": "All bookings fetched successfully",
  "bookings": [...],
  "total": 15
}</div>

                <table class="table">
                    <thead>
                        <tr>
                            <th>Booking Ref</th>
                            <th>Customer</th>
                            <th>Service</th>
                            <th>Scheduled</th>
                            <th>Status</th>
                            <th>Price</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>BK-20240515-A1B2C3D4</strong></td>
                            <td>John Doe (+919876543210)</td>
                            <td>Car Wash</td>
                            <td>2024-05-15 @ 10:30 AM</td>
                            <td><span class="badge badge-in-progress">In Progress</span></td>
                            <td>₹499</td>
                            <td>
                                <button class="btn btn-warning" style="font-size: 11px;">Assign</button>
                                <button class="btn btn-secondary" style="font-size: 11px;">View</button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>BK-20240514-X9Y8Z7W6</strong></td>
                            <td>Jane Smith (+919988776655)</td>
                            <td>Bike Wash</td>
                            <td>2024-05-14 @ 3:00 PM</td>
                            <td><span class="badge badge-completed">Completed</span></td>
                            <td>₹199</td>
                            <td>
                                <button class="btn btn-secondary" style="font-size: 11px;">View</button>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>BK-20240513-P5Q4R3S2</strong></td>
                            <td>Mike Johnson (+919876544321)</td>
                            <td>Car Wash</td>
                            <td>2024-05-13 @ 11:00 AM</td>
                            <td><span class="badge badge-pending">Pending</span></td>
                            <td>₹499</td>
                            <td>
                                <button class="btn btn-warning" style="font-size: 11px;">Assign</button>
                                <button class="btn btn-secondary" style="font-size: 11px;">View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <h3>Filter by Status</h3>
                <div class="form-group">
                    <label>Status</label>
                    <select onchange="filterBookings(this)">
                        <option value="">All Bookings</option>
                        <option value="pending">Pending</option>
                        <option value="assigned">Assigned</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>

                <div class="code-block">
GET /services/admin/bookings-by-status/pending
Authorization: Bearer {admin_access_token}

Valid statuses:
- pending: Not yet assigned
- assigned: Cleaner assigned, awaiting acceptance
- accepted: Cleaner accepted the job
- in_progress: Service in progress
- completed: Service completed
- cancelled: Booking cancelled</div>

                <h3>Statistics</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div class="card" style="text-align: center;">
                        <div style="font-size: 32px; color: #667eea; font-weight: bold;">47</div>
                        <div style="color: #666;">Total Bookings</div>
                    </div>
                    <div class="card" style="text-align: center;">
                        <div style="font-size: 32px; color: #4caf50; font-weight: bold;">12</div>
                        <div style="color: #666;">In Progress</div>
                    </div>
                    <div class="card" style="text-align: center;">
                        <div style="font-size: 32px; color: #ff9800; font-weight: bold;">8</div>
                        <div style="color: #666;">Pending</div>
                    </div>
                    <div class="card" style="text-align: center;">
                        <div style="font-size: 32px; color: #2196F3; font-weight: bold;">₹23,412</div>
                        <div style="color: #666;">Total Revenue</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- API Reference Tab -->
        <div class="content" id="api">
            <div class="section">
                <h2>📡 API Reference & Implementation Guide</h2>

                <h3>Base URL</h3>
                <div class="code-block">
http://localhost:8000/api  (Development)
https://api.washioo.com     (Production)</div>

                <h3>Authentication Headers</h3>
                <div class="code-block">
Authorization: Bearer {access_token}
Content-Type: application/json</div>

                <h3>Complete API Endpoints</h3>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /auth/send-otp</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PUBLIC</span>
                    </div>
                    <div>Send OTP to phone number</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /auth/signup</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PUBLIC</span>
                    </div>
                    <div>Signup new user OR add role to existing user</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /auth/signin</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PUBLIC</span>
                    </div>
                    <div>Login existing user</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /auth/refresh-token</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PROTECTED</span>
                    </div>
                    <div>Refresh access token using refresh token</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /auth/logout</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PROTECTED</span>
                    </div>
                    <div>Logout user (revoke refresh token)</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">GET /services/</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PROTECTED</span>
                    </div>
                    <div>Get all available services</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /services/address</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PROTECTED</span>
                    </div>
                    <div>Create new address</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">GET /services/addresses</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">PROTECTED</span>
                    </div>
                    <div>Get user's addresses</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">POST /services/book</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">CUSTOMER ONLY</span>
                    </div>
                    <div>Book a service</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">GET /services/my-bookings</span>
                        <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 3px; font-size: 11px;">CUSTOMER ONLY</span>
                    </div>
                    <div>Get customer's bookings</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">GET /services/admin/all-bookings</span>
                        <span style="background: #fff3e0; color: #e65100; padding: 5px 10px; border-radius: 3px; font-size: 11px;">ADMIN ONLY</span>
                    </div>
                    <div>View all bookings</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">GET /services/admin/bookings-by-status/{status}</span>
                        <span style="background: #fff3e0; color: #e65100; padding: 5px 10px; border-radius: 3px; font-size: 11px;">ADMIN ONLY</span>
                    </div>
                    <div>Filter bookings by status</div>
                </div>

                <h3>React Component Structure Example</h3>
                <div class="code-block">
// Suggested folder structure for React
src/
├── components/
│   ├── Auth/
│   │   ├── SendOTP.jsx
│   │   ├── SignupForm.jsx
│   │   └── SigninForm.jsx
│   ├── Services/
│   │   ├── ServiceList.jsx
│   │   └── ServiceCard.jsx
│   ├── Booking/
│   │   ├── BookingForm.jsx
│   │   ├── AddressSelector.jsx
│   │   └── BookingSummary.jsx
│   ├── Dashboard/
│   │   ├── CustomerDashboard.jsx
│   │   ├── AdminDashboard.jsx
│   │   └── BookingsList.jsx
│   └── Common/
│       ├── Header.jsx
│       ├── Navbar.jsx
│       └── ErrorBoundary.jsx
├── services/
│   ├── authService.js
│   ├── bookingService.js
│   └── apiClient.js
├── context/
│   ├── AuthContext.jsx
│   └── BookingContext.jsx
├── hooks/
│   ├── useAuth.js
│   └── useBooking.js
└── pages/
    ├── HomePage.jsx
    ├── BookingPage.jsx
    └── DashboardPage.jsx</div>

                <h3>Important Notes for Frontend</h3>
                <ul style="line-height: 2; color: #333;">
                    <li>✅ Store <code style="background: #f0f0f0; padding: 2px 5px;">access_token</code> in memory or sessionStorage (not localStorage for security)</li>
                    <li>✅ Store <code style="background: #f0f0f0; padding: 2px 5px;">refresh_token</code> in httpOnly cookie if possible</li>
                    <li>✅ Refresh access token before expiry (use interceptors)</li>
                    <li>✅ Handle 401 errors by refreshing token and retrying request</li>
                    <li>✅ Always check <code style="background: #f0f0f0; padding: 2px 5px;">is_new_user</code> flag after signup</li>
                    <li>✅ Validate all user inputs on frontend before sending to API</li>
                    <li>✅ Show loading states and error messages clearly</li>
                    <li>✅ Implement proper error handling for all API calls</li>
                    <li>✅ Use axios/fetch with timeout configuration</li>
                    <li>✅ Implement proper role-based routing</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        function showTab(event, tabName) {
            // Hide all content
            const contents = document.querySelectorAll('.content');
            contents.forEach(content => content.classList.remove('active'));

            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));

            // Show selected content
            document.getElementById(tabName).classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function sendOTP(event) {
            event.preventDefault();
            const phone = document.getElementById('phone').value;
            alert(`✅ OTP sent to ${phone}\n\nIn React:\nawait authService.sendOTP(phone);\nResponse: { message: "OTP sent", user_exist: true/false }`);
        }

        function signup(event) {
            event.preventDefault();
            alert(`✅ Signup/Add Role initiated!\n\nFlow logic:\n- If user_exist = false → New user signup\n- If user_exist = true → Add role to existing user`);
        }

        function signin(event) {
            event.preventDefault();
            alert(`✅ Sign in successful!\n\nTokens stored. Redirect to dashboard based on role.`);
        }

        function toggleAddressForm() {
            const form = document.getElementById('addressForm');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function createAddress(event) {
            event.preventDefault();
            alert('✅ Address created successfully!');
            toggleAddressForm();
        }

        function selectService(element) {
            document.querySelectorAll('.service-card').forEach(card => {
                card.classList.remove('selected');
            });
            element.classList.add('selected');
            alert('✅ Service selected! Now proceed to booking.');
        }

        function selectAddress(element) {
            document.querySelectorAll('.address-item').forEach(item => {
                item.classList.remove('selected');
            });
            element.classList.add('selected');
            alert('✅ Address selected!');
        }

        function filterBookings(select) {
            const status = select.value;
            if (status) {
                alert(`🔍 Filtering bookings by status: ${status}\n\nAPI Call: GET /services/admin/bookings-by-status/${status}`);
            }
        }
    </script>
</body>
</html>