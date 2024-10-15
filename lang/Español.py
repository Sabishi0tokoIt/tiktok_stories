# Diccionario de Idiomas
country_map = {
    'España': 'es-ES',
    'Estados Unidos': 'es-US'
}

# Diccionario de Géneros
gender_map = {
    'Masculino': 'MALE',
    'Femenino': 'FEMALE'
}
    
# Diccionarios de estilos de voces
style_map = {    
    'Neural' : 'Neural',
    'Estudio' : 'Studio',
    'Estándar' : 'Standard',
    'Wavenet' : 'Wavenet',
    'Políglota' : 'Polyglot',
    'Noticias' : 'News'
}
    
# Diccionario de configuración de voces
voices_map = {
    'es-ES': {
        'MALE': {
            'Neural': {'Voz 1': '2-B', 'Voz 2': '2-F'},
            'Standard': {'Voz 1': '-B'},
            'Studio': {'Voz 1': '-F'},
            'Wavenet': {'Voz 1': '-B'},
            'Polyglot': {'Voz 1': '-1'},
        },
        'FEMALE': {
            'Neural': {'Voz 1': '2-A', 'Voz 2': '2-C', 'Voz 3': '2-D', 'Voz 4': '2-E'},
            'Standard': {'Voz 1': '-A', 'Voz 2': '-C', 'Voz 3': '-D'},
            'Studio': {'Voz 1': '-C'},
            'Wavenet': {'Voz 1': '-C', 'Voz 2': '-D'},
        }
    },
    'es-US': {
        'MALE': {
            'Neural': {'Voz 1': '2-B', 'Voz 2': '2-C'},
            'Standard': {'Voz 1': '-B', 'Voz 2': '-C'},
            'Studio': {'Voz 1': '-B'},
            'Wavenet': {'Voz 1': '-B', 'Voz 2': '-C'},
            'Polyglot': {'Voz 1': '-1'},
            'News': {'Voz 1': '-D', 'Voz 2': '-E'}
        },
        'FEMALE': {
            'Neural': {'Voz 1': '2-A'},
            'Standard': {'Voz 1': '-A'},
            'Wavenet': {'Voz 1': '-A'},
            'News': {'Voz 1': '-F', 'Voz 2': '-G'}
        }
    }
}

