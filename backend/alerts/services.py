RECOMMENDATIONS = {
    'TEMPERATURE': {
        'LOW': 'Monitorar a temperatura da maquina com atencao nas proximas horas.',
        'MEDIUM': 'Verificar o sistema de refrigeracao e reducao da carga operacional.',
        'HIGH': 'Parar a maquina imediatamente e inspecionar o sistema de refrigeracao.',
    },
    'VIBRATION': {
        'LOW': 'Verificar fixacoes e parafusos da maquina.',
        'MEDIUM': 'Inspecionar rolamentos e componentes mecanicos em movimento.',
        'HIGH': 'Parar a maquina imediatamente. Risco de dano estrutural.',
    },
    'PRESSURE': {
        'LOW': 'Monitorar niveis de pressao e verificar possiveis obstrucoes.',
        'MEDIUM': 'Verificar valvulas e conexoes do sistema de pressao.',
        'HIGH': 'Aliviar pressao imediatamente e inspecionar todo o sistema hidraulico.',
    },
    'HUMIDITY': {
        'LOW': 'Verificar vedacoes e condicoes ambientais.',
        'MEDIUM': 'Inspecionar isolamentos eletricos e sistema de exaustao.',
        'HIGH': 'Parar a maquina e secar componentes internos antes de religar.',
    },
    'CURRENT': {
        'LOW': 'Verificar consumo eletrico e possiveis sobrecargas.',
        'MEDIUM': 'Inspecionar cabos, disjuntores e motores eletricos.',
        'HIGH': 'Desligar imediatamente. Risco de curto-circuito ou incendio.',
    },
    'VOLTAGE': {
        'LOW': 'Verificar estabilidade da rede eletrica e reguladores de tensao.',
        'MEDIUM': 'Inspecionar fonte de alimentacao e estabilizadores.',
        'HIGH': 'Desligar equipamentos da rede. Risco de danos aos componentes eletronicos.',
    },
    'RPM': {
        'LOW': 'Verificar motor e carga do sistema.',
        'MEDIUM': 'Inspecionar correias, engrenagens e sistema de transmissao.',
        'HIGH': 'Parar a maquina e inspecionar todo o mecanismo de transmissao.',
    },
    'OTHER': {
        'LOW': 'Monitorar o sensor e registrar ocorrencias.',
        'MEDIUM': 'Realizar inspecao preventiva na maquina.',
        'HIGH': 'Parar a maquina e realizar manutencao corretiva imediata.',
    },
}


def get_risk_level(anomaly_score):
    if anomaly_score is None:
        return 'LOW'
    if anomaly_score < 20:
        return 'LOW'
    if anomaly_score < 50:
        return 'MEDIUM'
    return 'HIGH'


def get_recommendation(sensor_type, risk_level):
    sensor_recommendations = RECOMMENDATIONS.get(sensor_type, RECOMMENDATIONS['OTHER'])
    return sensor_recommendations.get(risk_level, sensor_recommendations['LOW'])
