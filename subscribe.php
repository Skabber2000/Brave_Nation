<?php
/**
 * Nação Valente — Newsletter subscription endpoint
 * Hardened: rate limiting, honeypot, CORS lock, input validation, no error leaks
 */

// ── Security headers ──
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: strict-origin-when-cross-origin');

// ── CORS: only allow our own domain ──
$allowed_origins = ['https://nacaovalente.com.pt', 'http://nacaovalente.com.pt'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins, true)) {
    header("Access-Control-Allow-Origin: $origin");
}
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// ── Rate limiting (file-based, 5 requests per IP per hour) ──
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$rate_dir = __DIR__ . '/rate_limit';
if (!is_dir($rate_dir)) {
    mkdir($rate_dir, 0700, true);
}
$rate_file = $rate_dir . '/' . md5($ip) . '.json';
$rate_window = 3600; // 1 hour
$rate_max = 5;

$now = time();
$attempts = [];
if (file_exists($rate_file)) {
    $attempts = json_decode(file_get_contents($rate_file), true) ?: [];
    $attempts = array_filter($attempts, fn($t) => $t > $now - $rate_window);
}
if (count($attempts) >= $rate_max) {
    http_response_code(429);
    echo json_encode(['success' => false, 'error' => 'Demasiados pedidos. Tente novamente mais tarde.']);
    exit;
}
$attempts[] = $now;
file_put_contents($rate_file, json_encode(array_values($attempts)), LOCK_EX);

// ── Parse input ──
$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Pedido inválido']);
    exit;
}

// ── Honeypot check (bot trap) ──
if (!empty($input['website'])) {
    // Bots fill hidden fields — silently reject
    echo json_encode(['success' => true, 'message' => 'Subscrito com sucesso']);
    exit;
}

// ── Validate email ──
$email = isset($input['email']) ? trim($input['email']) : '';
if (!$email || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Email inválido']);
    exit;
}
// Max length guard
if (strlen($email) > 254) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Email inválido']);
    exit;
}

// ── Database ──
$db_host = 'localhost';
$db_name = 'c15valente';
$db_user = 'c15valente';
$db_pass = 'trwyJCS@84';

try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8mb4", $db_user, $db_pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_EMULATE_PREPARES => false
    ]);

    $pdo->exec("CREATE TABLE IF NOT EXISTS subscribers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip VARCHAR(45),
        source VARCHAR(50) DEFAULT 'website'
    )");

    $stmt = $pdo->prepare("INSERT IGNORE INTO subscribers (email, ip) VALUES (:email, :ip)");
    $stmt->execute([
        ':email' => $email,
        ':ip' => $ip
    ]);

    if ($stmt->rowCount() > 0) {
        echo json_encode(['success' => true, 'message' => 'Subscrito com sucesso']);
    } else {
        echo json_encode(['success' => true, 'message' => 'Email já registado']);
    }

} catch (PDOException $e) {
    // Never leak DB errors to client
    error_log('NV subscribe error: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Erro interno']);
}
