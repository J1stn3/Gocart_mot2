-- SMS Messages Seeders for gocart_db
-- Copy and paste this into MySQL (Laragon)

-- IMPORTANT: Delete old data first (REQUIRED)
DELETE FROM sms_messages;

-- Insert new SMS messages
INSERT INTO sms_messages (user_id, phone_number, message, status, sent_at, delivered_at, created_at, updated_at) VALUES
(1, '09510362349', 'Your order #1001 has been confirmed!', 'DELIVERED', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY),
(1, '09510362349', 'Your order is being prepared for shipment.', 'SENT', NOW() - INTERVAL 23 HOUR, NULL, NOW() - INTERVAL 23 HOUR, NOW() - INTERVAL 23 HOUR),
(1, '09510362349', 'Your order has been shipped.', 'PENDING', NULL, NULL, NOW() - INTERVAL 22 HOUR, NOW() - INTERVAL 22 HOUR),
(2, '09510362349', 'Welcome to GoCart! Account created successfully.', 'DELIVERED', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY),
(2, '09510362349', 'Your verification code is 445612', 'SENT', NOW() - INTERVAL 21 HOUR, NOW() - INTERVAL 21 HOUR, NOW() - INTERVAL 21 HOUR, NOW() - INTERVAL 21 HOUR),
(3, '09510362349', 'Flash sale: 50% off today only!', 'DELIVERED', NOW() - INTERVAL 20 HOUR, NOW() - INTERVAL 20 HOUR, NOW() - INTERVAL 20 HOUR, NOW() - INTERVAL 20 HOUR),
(3, '09510362349', 'New products have arrived in your cart.', 'SENT', NOW() - INTERVAL 19 HOUR, NULL, NOW() - INTERVAL 19 HOUR, NOW() - INTERVAL 19 HOUR),
(4, '09510362349', 'Your payment has been received.', 'DELIVERED', NOW() - INTERVAL 18 HOUR, NOW() - INTERVAL 18 HOUR, NOW() - INTERVAL 18 HOUR, NOW() - INTERVAL 18 HOUR),
(4, '09510362349', 'Your order is out for delivery.', 'SENT', NOW() - INTERVAL 17 HOUR, NULL, NOW() - INTERVAL 17 HOUR, NOW() - INTERVAL 17 HOUR),
(5, '09510362349', 'Order #1002 confirmed successfully.', 'DELIVERED', NOW() - INTERVAL 16 HOUR, NOW() - INTERVAL 16 HOUR, NOW() - INTERVAL 16 HOUR, NOW() - INTERVAL 16 HOUR),
(1, '09510362349', 'Your package will arrive tomorrow.', 'SENT', NOW() - INTERVAL 15 HOUR, NULL, NOW() - INTERVAL 15 HOUR, NOW() - INTERVAL 15 HOUR),
(2, '09510362349', 'Delivery attempt failed, retry scheduled.', 'PENDING', NULL, NULL, NOW() - INTERVAL 14 HOUR, NOW() - INTERVAL 14 HOUR),
(3, '09510362349', 'Your refund has been processed.', 'DELIVERED', NOW() - INTERVAL 13 HOUR, NOW() - INTERVAL 13 HOUR, NOW() - INTERVAL 13 HOUR, NOW() - INTERVAL 13 HOUR),
(4, '09510362349', 'Special promo just for you!', 'SENT', NOW() - INTERVAL 12 HOUR, NULL, NOW() - INTERVAL 12 HOUR, NOW() - INTERVAL 12 HOUR),
(5, '09510362349', 'Your cart is waiting for checkout.', 'PENDING', NULL, NULL, NOW() - INTERVAL 11 HOUR, NOW() - INTERVAL 11 HOUR),
(1, '09510362349', 'Order update: packaging completed.', 'DELIVERED', NOW() - INTERVAL 10 HOUR, NOW() - INTERVAL 10 HOUR, NOW() - INTERVAL 10 HOUR, NOW() - INTERVAL 10 HOUR),
(2, '09510362349', 'Limited time offer ends soon!', 'SENT', NOW() - INTERVAL 9 HOUR, NULL, NOW() - INTERVAL 9 HOUR, NOW() - INTERVAL 9 HOUR),
(3, '09510362349', 'Your item is ready for pickup.', 'DELIVERED', NOW() - INTERVAL 8 HOUR, NOW() - INTERVAL 8 HOUR, NOW() - INTERVAL 8 HOUR, NOW() - INTERVAL 8 HOUR),
(4, '09510362349', 'Security alert: new login detected.', 'SENT', NOW() - INTERVAL 7 HOUR, NULL, NOW() - INTERVAL 7 HOUR, NOW() - INTERVAL 7 HOUR),
(5, '09510362349', 'Order confirmed and processing.', 'PENDING', NULL, NULL, NOW() - INTERVAL 6 HOUR, NOW() - INTERVAL 6 HOUR);

-- Verify inserted data
SELECT * FROM sms_messages;