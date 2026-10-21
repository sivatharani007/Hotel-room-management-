-- ========================================================
-- GRANDSTAY HOTEL ROOM MANAGEMENT SYSTEM
-- Database Initialization & Schema Script
-- ========================================================

-- Create database if it does not already exist
CREATE DATABASE IF NOT EXISTS `hotel_management`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `hotel_management`;

-- ========================================================
-- 1. TABLE: customers
-- ========================================================
CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `address` TEXT,
    `id_type` VARCHAR(50) DEFAULT 'Passport / National ID',
    `id_number` VARCHAR(50),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_cust_phone` (`phone`),
    INDEX `idx_cust_email` (`email`),
    INDEX `idx_cust_name` (`full_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================================
-- 2. TABLE: rooms
-- ========================================================
CREATE TABLE IF NOT EXISTS `rooms` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `room_number` VARCHAR(20) NOT NULL UNIQUE,
    `room_type` ENUM('Standard', 'Deluxe', 'Suite', 'Family Room') NOT NULL DEFAULT 'Standard',
    `price_per_night` DECIMAL(10, 2) NOT NULL,
    `capacity` INT NOT NULL DEFAULT 2,
    `description` TEXT,
    `status` ENUM('Available', 'Occupied', 'Maintenance') NOT NULL DEFAULT 'Available',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_room_status` (`status`),
    INDEX `idx_room_type` (`room_type`),
    INDEX `idx_room_price` (`price_per_night`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================================
-- 3. TABLE: bookings
-- ========================================================
CREATE TABLE IF NOT EXISTS `bookings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `booking_code` VARCHAR(30) NOT NULL UNIQUE,
    `customer_id` INT NOT NULL,
    `room_id` INT NOT NULL,
    `check_in` DATE NOT NULL,
    `check_out` DATE NOT NULL,
    `guests` INT NOT NULL DEFAULT 1,
    `price_per_night` DECIMAL(10, 2) NOT NULL,
    `total_amount` DECIMAL(10, 2) NOT NULL,
    `status` ENUM('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED') NOT NULL DEFAULT 'CONFIRMED',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `cancelled_at` TIMESTAMP NULL DEFAULT NULL,
    `checked_out_at` TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT `fk_bookings_customer` FOREIGN KEY (`customer_id`) 
        REFERENCES `customers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT `fk_bookings_room` FOREIGN KEY (`room_id`) 
        REFERENCES `rooms` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX `idx_booking_dates` (`check_in`, `check_out`),
    INDEX `idx_booking_status` (`status`),
    INDEX `idx_booking_code` (`booking_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================================
-- 4. TABLE: payments
-- ========================================================
CREATE TABLE IF NOT EXISTS `payments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `booking_id` INT NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL,
    `payment_status` ENUM('Pending', 'Paid', 'Refunded') NOT NULL DEFAULT 'Pending',
    `payment_method` VARCHAR(50) DEFAULT 'Credit Card',
    `payment_date` TIMESTAMP NULL DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_payments_booking` FOREIGN KEY (`booking_id`) 
        REFERENCES `bookings` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX `idx_payment_status` (`payment_status`),
    INDEX `idx_payment_booking` (`booking_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================================
-- DEMONSTRATION SEED DATA
-- (Clearly identified sample records for preview and testing)
-- ========================================================

-- Insert Sample Rooms (12 diverse rooms across floors 1 to 4)
INSERT IGNORE INTO `rooms` (`id`, `room_number`, `room_type`, `price_per_night`, `capacity`, `description`, `status`) VALUES
(1, '101', 'Standard', 89.00, 2, 'Cozy single room with queen bed, modern work desk, high-speed Wi-Fi, and courtyard view.', 'Available'),
(2, '102', 'Standard', 89.00, 2, 'Well-appointed standard room featuring queen bed, smart TV, tea maker, and ensuite bath.', 'Available'),
(3, '103', 'Standard', 95.00, 2, 'Quiet garden-side room with soundproof glazing, rain shower, and complimentary breakfast.', 'Maintenance'),
(4, '201', 'Deluxe', 149.00, 3, 'Spacious deluxe room with king bed, balcony with city view, minibar, and luxury bath amenities.', 'Occupied'),
(5, '202', 'Deluxe', 149.00, 3, 'Corner deluxe room with panoramic skyline views, plush sofa bed, and premium espresso maker.', 'Available'),
(6, '203', 'Deluxe', 159.00, 3, 'Executive deluxe room with ergonomic workstation, king pillowtop bed, and deep soaking tub.', 'Available'),
(7, '301', 'Suite', 249.00, 4, 'Luxurious presidential junior suite with separate master bedroom, living lounge, and Jacuzzi.', 'Occupied'),
(8, '302', 'Suite', 279.00, 4, 'Signature skyline suite with floor-to-ceiling windows, marble bathroom, and butler pantry.', 'Available'),
(9, '303', 'Suite', 299.00, 4, 'Royal penthouse suite with private terrace, king canopy bed, dining area, and 65-inch OLED TV.', 'Available'),
(10, '401', 'Family Room', 189.00, 5, 'Spacious multi-bed family suite with 1 king bed and 2 twin beds, kids entertainment zone.', 'Available'),
(11, '402', 'Family Room', 199.00, 6, 'Interconnected family haven with 2 queen beds, sofa bed, kitchenette, and dual vanity bath.', 'Available'),
(12, '403', 'Family Room', 185.00, 5, 'Comfortable family room with balcony, bunk beds for children, board games, and mini-fridge.', 'Maintenance');

-- Insert Sample Demonstration Customers
INSERT IGNORE INTO `customers` (`id`, `full_name`, `phone`, `email`, `address`, `id_type`, `id_number`) VALUES
(1, 'Alexander Wright', '+1 (555) 234-5678', 'a.wright@example.com', '124 Blossom Hill Rd, Seattle, WA', 'Passport', 'P9842103'),
(2, 'Sophia Martinez', '+1 (555) 876-5432', 'sophia.m@example.com', '540 Ocean Boulevard, San Diego, CA', 'Driver License', 'DL452901B'),
(3, 'David Chen', '+1 (555) 345-6789', 'dchen.tech@example.com', '88 Innovation Way, Austin, TX', 'National ID', 'NID-882103'),
(4, 'Emma Watson-Bell', '+1 (555) 901-2345', 'emma.bell@example.com', '32 Oxford Crescent, Boston, MA', 'Passport', 'P7721590'),
(5, 'Marcus Sterling', '+1 (555) 678-9012', 'm.sterling@example.com', '700 Wall St, New York, NY', 'Passport', 'P1192834');

-- Insert Sample Demonstration Bookings (Covering different statuses)
-- Note: Dates can be updated dynamically or serve as initial records
INSERT IGNORE INTO `bookings` (`id`, `booking_code`, `customer_id`, `room_id`, `check_in`, `check_out`, `guests`, `price_per_night`, `total_amount`, `status`, `created_at`, `checked_out_at`) VALUES
(1, 'GS-20261015-001', 1, 4, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 2, 149.00, 447.00, 'CHECKED_IN', DATE_SUB(NOW(), INTERVAL 5 DAY), NULL),
(2, 'GS-20261018-002', 2, 7, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 3, 249.00, 996.00, 'CHECKED_IN', DATE_SUB(NOW(), INTERVAL 3 DAY), NULL),
(3, 'GS-20261010-003', 3, 1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), DATE_SUB(CURDATE(), INTERVAL 3 DAY), 1, 89.00, 356.00, 'CHECKED_OUT', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(4, 'GS-20261022-004', 4, 5, DATE_ADD(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 2, 149.00, 447.00, 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(5, 'GS-20261012-005', 5, 2, DATE_SUB(CURDATE(), INTERVAL 4 DAY), DATE_SUB(CURDATE(), INTERVAL 1 DAY), 2, 89.00, 267.00, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 6 DAY), NULL);

-- Insert Sample Payments corresponding to bookings
INSERT IGNORE INTO `payments` (`id`, `booking_id`, `amount`, `payment_status`, `payment_method`, `payment_date`) VALUES
(1, 1, 447.00, 'Paid', 'Credit Card', NOW()),
(2, 2, 996.00, 'Paid', 'Bank Transfer', NOW()),
(3, 3, 356.00, 'Paid', 'Debit Card', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(4, 4, 447.00, 'Pending', 'Credit Card', NULL),
(5, 5, 267.00, 'Refunded', 'Credit Card', DATE_SUB(NOW(), INTERVAL 4 DAY));
