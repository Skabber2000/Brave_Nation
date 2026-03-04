<?php
/**
 * Nação Valente — Subscriber Admin Panel
 * Password-protected. Brute-force throttled.
 */
session_start();

// ── Config ──
$admin_password_hash = password_hash('NV_admin_2026!', PASSWORD_DEFAULT);
// After first deploy, replace the line above with a hardcoded hash:
// $admin_password_hash = '$2y$10$...';

$db_host = 'localhost';
$db_name = 'c15valente';
$db_user = 'c15valente';
$db_pass = 'trwyJCS@84';

// ── Brute-force protection (5 attempts per IP per 15 min) ──
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$rate_dir = __DIR__ . '/rate_limit';
if (!is_dir($rate_dir)) mkdir($rate_dir, 0700, true);
$rate_file = $rate_dir . '/admin_' . md5($ip) . '.json';
$rate_window = 900;
$rate_max = 5;

function check_rate_limit(): bool {
    global $rate_file, $rate_window, $rate_max;
    $now = time();
    $attempts = [];
    if (file_exists($rate_file)) {
        $attempts = json_decode(file_get_contents($rate_file), true) ?: [];
        $attempts = array_filter($attempts, fn($t) => $t > $now - $rate_window);
    }
    return count($attempts) < $rate_max;
}

function record_attempt(): void {
    global $rate_file, $rate_window;
    $now = time();
    $attempts = [];
    if (file_exists($rate_file)) {
        $attempts = json_decode(file_get_contents($rate_file), true) ?: [];
        $attempts = array_filter($attempts, fn($t) => $t > $now - $rate_window);
    }
    $attempts[] = $now;
    file_put_contents($rate_file, json_encode(array_values($attempts)), LOCK_EX);
}

// ── Logout ──
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: admin.php');
    exit;
}

// ── Login ──
$login_error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['password'])) {
    if (!check_rate_limit()) {
        $login_error = 'Demasiadas tentativas. Aguarde 15 minutos.';
    } else {
        // Verify against stored hash — regenerate hash on first use
        if (password_verify($_POST['password'], $admin_password_hash) || $_POST['password'] === 'NV_admin_2026!') {
            $_SESSION['nv_admin'] = true;
            $_SESSION['nv_admin_time'] = time();
            header('Location: admin.php');
            exit;
        } else {
            record_attempt();
            $login_error = 'Password incorreta.';
        }
    }
}

// Session timeout: 30 minutes
if (isset($_SESSION['nv_admin_time']) && time() - $_SESSION['nv_admin_time'] > 1800) {
    session_destroy();
    header('Location: admin.php');
    exit;
}

$logged_in = !empty($_SESSION['nv_admin']);

// ── CSV Export ──
if ($logged_in && isset($_GET['export']) && $_GET['export'] === 'csv') {
    try {
        $pdo = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8mb4", $db_user, $db_pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_EMULATE_PREPARES => false
        ]);
        $stmt = $pdo->query("SELECT email, subscribed_at, source FROM subscribers ORDER BY subscribed_at DESC");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="subscribers_' . date('Y-m-d') . '.csv"');
        $out = fopen('php://output', 'w');
        fputcsv($out, ['Email', 'Data', 'Fonte']);
        foreach ($rows as $row) {
            fputcsv($out, [$row['email'], $row['subscribed_at'], $row['source']]);
        }
        fclose($out);
        exit;
    } catch (PDOException $e) {
        error_log('NV admin export error: ' . $e->getMessage());
        die('Erro ao exportar.');
    }
}

// ── Fetch subscribers ──
$subscribers = [];
$total = 0;
$db_error = '';
if ($logged_in) {
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
        $stmt = $pdo->query("SELECT id, email, subscribed_at, source FROM subscribers ORDER BY subscribed_at DESC");
        $subscribers = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $total = count($subscribers);
    } catch (PDOException $e) {
        error_log('NV admin error: ' . $e->getMessage());
        $db_error = 'Erro ao aceder à base de dados.';
    }
}
?>
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Admin — Nação Valente</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f0e8; color: #2c2c2c; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    .login-box { background: #fff; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 380px; width: 90%; text-align: center; }
    .login-box h1 { font-family: Georgia, serif; color: #1a1a2e; margin-bottom: 0.5rem; font-size: 1.4rem; }
    .login-box p { color: #888; font-size: 0.85rem; margin-bottom: 1.5rem; }
    .login-box input[type="password"] { width: 100%; padding: 0.75rem 1rem; border: 2px solid #ddd; border-radius: 8px; font-size: 1rem; margin-bottom: 1rem; }
    .login-box input:focus { outline: none; border-color: #C5A55A; }
    .login-box button { width: 100%; padding: 0.75rem; background: #1a1a2e; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
    .login-box button:hover { background: #2a2a4e; }
    .error { color: #c0392b; font-size: 0.85rem; margin-bottom: 1rem; }

    .admin { max-width: 900px; width: 95%; margin: 2rem auto; }
    .admin body { align-items: flex-start; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
    .header h1 { font-family: Georgia, serif; color: #1a1a2e; font-size: 1.5rem; }
    .header .actions { display: flex; gap: 0.75rem; }
    .btn { padding: 0.5rem 1.2rem; border-radius: 8px; text-decoration: none; font-size: 0.85rem; border: none; cursor: pointer; }
    .btn-gold { background: #C5A55A; color: #fff; }
    .btn-gold:hover { background: #b8953f; }
    .btn-outline { background: transparent; border: 1px solid #ccc; color: #666; }
    .btn-outline:hover { border-color: #999; color: #333; }
    .stat { background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 1.5rem; text-align: center; }
    .stat .num { font-size: 2.5rem; font-weight: 700; color: #C5A55A; }
    .stat .label { color: #888; font-size: 0.85rem; }
    table { width: 100%; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-collapse: collapse; }
    th { background: #1a1a2e; color: #fff; padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
    td { padding: 0.75rem 1rem; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #faf8f4; }
    .empty { text-align: center; padding: 3rem; color: #999; }
</style>
</head>
<body>

<?php if (!$logged_in): ?>
<div class="login-box">
    <h1>Nação Valente</h1>
    <p>Painel de administração</p>
    <?php if ($login_error): ?>
        <div class="error"><?= htmlspecialchars($login_error) ?></div>
    <?php endif; ?>
    <form method="POST">
        <input type="password" name="password" placeholder="Password" autofocus required>
        <button type="submit">Entrar</button>
    </form>
</div>

<?php else: ?>
<div class="admin">
    <div class="header">
        <h1>Subscritores da Newsletter</h1>
        <div class="actions">
            <a href="admin.php?export=csv" class="btn btn-gold">Exportar CSV</a>
            <a href="/" class="btn btn-outline">Ver site</a>
            <a href="admin.php?logout=1" class="btn btn-outline">Sair</a>
        </div>
    </div>

    <?php if ($db_error): ?>
        <div class="error"><?= htmlspecialchars($db_error) ?></div>
    <?php else: ?>
        <div class="stat">
            <div class="num"><?= $total ?></div>
            <div class="label">subscritores</div>
        </div>

        <?php if ($total > 0): ?>
        <table>
            <thead>
                <tr><th>#</th><th>Email</th><th>Data</th><th>Fonte</th></tr>
            </thead>
            <tbody>
                <?php foreach ($subscribers as $s): ?>
                <tr>
                    <td><?= (int)$s['id'] ?></td>
                    <td><?= htmlspecialchars($s['email']) ?></td>
                    <td><?= htmlspecialchars($s['subscribed_at']) ?></td>
                    <td><?= htmlspecialchars($s['source']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
            <div class="empty">Ainda não há subscritores.</div>
        <?php endif; ?>
    <?php endif; ?>
</div>
<?php endif; ?>

</body>
</html>
