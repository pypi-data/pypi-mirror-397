PYTHON_VULN_RULES = {
    "eval_exec_usage": {
        "name": "eval() y exec() Usage",
        "severity": "critical",
        "patterns": [
            r"\beval\s*\(",
            r"\bexec\s*\(",
            r"\bcompile\s*\(",
            r"__import__\s*\(",
            r"exec\s*\(",
            r"eval\s*\(\s*input\s*\(",
            r"exec\s*\(\s*input\s*\(",
            r"compile\s*\(\s*.*\bexec\b",
            r"ast\.literal_eval\s*\(\s*(?![\s]*\[|[\s]*\{)",
            r"pickle\.loads\s*\(",
        ],
        "description": "eval() y exec() ejecutan código Python arbitrario, permitiendo inyección de código malicioso",
        "recommendations": [
            "Nunca usar eval() o exec() con entrada del usuario",
            "Para evaluar expresiones, usar ast.literal_eval() solo con literales",
            "Para JSON, usar json.loads() en lugar de eval()",
            "Para configuración, usar bibliotecas como configparser",
            "Considerar usar sandboxes como RestrictedPython",
            "Implementar whitelisting de funciones permitidas"
        ]
    },
    
    "hardcoded_secrets": {
        "name": "Secretos hardcodeados",
        "severity": "critical",
        "patterns": [
            r"(?:password|passwd|pwd)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:api_key|apiKey|API_KEY)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:secret|SECRET|secret_key|secretKey)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:token|TOKEN|access_token|accessToken)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:db_password|dbPassword|DB_PASSWORD)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:django\.db\.backends\.postgresql|mysql|oracle).*password.*['\"][^'\"]+['\"]",
            r"os\.environ\[[\s]*['\"](?:SECRET|PASSWORD|API|TOKEN)",
            r"settings\.\w*\s*=\s*['\"](?:sk_|pk_|ghp_)[^'\"]*['\"]",
            r"DATABASE_URL\s*=\s*['\"].*:.*@",
            r"(?:aws_access_key|AWS_ACCESS_KEY|aws_secret|AWS_SECRET)\s*[=:]\s*['\"]",
        ],
        "description": "Credenciales, claves API, tokens y secretos expuestos en código fuente",
        "recommendations": [
            "Usar variables de entorno (.env) para almacenar secretos",
            "Usar python-dotenv para cargar variables de entorno",
            "Implementar gestores de secretos como AWS Secrets Manager",
            "Nunca commitar archivos .env al repositorio",
            "Usar .gitignore para excluir archivos con credenciales",
            "Rotar todas las credenciales encontradas inmediatamente"
        ]
    },
    
    "sql_injection": {
        "name": "SQL Injection",
        "severity": "critical",
        "patterns": [
            r"(?:query|execute|executemany)\s*\(\s*['\"].*(?:\+|\.format|\%|f[\s]*['\"]|\$\{).*['\"]",
            r"f[\s]*['\"]SELECT.*\{.*\}",
            r"(?:cursor|conn)\.execute\s*\(\s*['\"].*(?:\+|\.format|\%|f[\s]*[\'\"])",
            r"db\.query\s*\(\s*['\"].*(?:\+|\.format).*['\"]",
            r"SELECT\s+.*\+\s*str\(",
            r"INSERT\s+INTO\s+.*\+\s*(?:str|format)",
            r"UPDATE\s+.*\+\s*(?:str|format)",
            r"DELETE\s+FROM\s+.*\+\s*(?:str|format)",
            r"\.execute\s*\(\s*['\"].*\%.*['\"],\s*(?:.*user|.*input)",
            r"sqlalchemy\.text\s*\(\s*['\"].*\{.*\}['\"]",
        ],
        "description": "Concatenación de variables en consultas SQL sin usar prepared statements, vulnerables a inyección SQL",
        "recommendations": [
            "Usar prepared statements con parametrización",
            "Usar ORMs como SQLAlchemy, Django ORM o Tortoise",
            "Usar ? para placeholders en lugar de concatenación",
            "Validar y sanitizar todas las entradas del usuario",
            "Usar whitelist de valores permitidos",
            "Implementar principio de menos privilegios en conexiones DB"
        ]
    },
    
    "command_injection": {
        "name": "Command Injection",
        "severity": "critical",
        "patterns": [
            r"(?:os\.system|os\.popen|subprocess\.call|subprocess\.Popen)\s*\(\s*['\"].*(?:\+|\.format|f[\s]*[\'\"]|\.split\(\))",
            r"subprocess\.(?:call|run|Popen)\s*\(\s*['\"].*\+",
            r"os\.system\s*\(\s*f[\s]*['\"].*\{",
            r"shell\s*=\s*True[\s\S]*?subprocess\.(?:call|run|Popen)",
            r"subprocess\.shell\s*\([\s\S]*?True",
            r"os\.popen\s*\(\s*(?:cmd|command|args)\s*\+",
            r"exec\s*\(\s*f[\s]*['\"].*\{.*\}",
            r"__import__\s*\(\s*['\"]subprocess['\"][\s\S]*?os\.system",
            r"paramiko\.exec_command\s*\(\s*['\"].*\+",
            r"fabric\.run\s*\(\s*['\"].*\+",
        ],
        "description": "Ejecución de comandos del sistema con variables sin validar, permite command injection",
        "recommendations": [
            "Evitar os.system(), usar subprocess con lista de argumentos",
            "Nunca pasar shell=True si usa entrada del usuario",
            "Usar subprocess.run() con lista de argumentos separados",
            "Validar y sanitizar todas las entradas de usuario",
            "Usar whitelist de comandos permitidos",
            "Implementar least privilege para procesos ejecutados"
        ]
    },
    
    "insecure_deserialization": {
        "name": "Insecure Deserialization",
        "severity": "critical",
        "patterns": [
            r"pickle\.load\s*\(",
            r"pickle\.loads\s*\(",
            r"yaml\.load\s*\(",
            r"yaml\.unsafe_load\s*\(",
            r"marshal\.load\s*\(",
            r"dill\.load\s*\(",
            r"cloudpickle\.load\s*\(",
            r"joblib\.load\s*\(",
            r"(?:flask|django)\.request\.(?:data|form|json)",
            r"shelve\.open\s*\(",
        ],
        "description": "Desserialización insegura de objetos Python permite ejecución de código arbitrario",
        "recommendations": [
            "Usar json.loads() en lugar de pickle para datos untrusted",
            "Si debe usar pickle, validar fuente de datos",
            "Usar yaml.safe_load() en lugar de yaml.load()",
            "Implementar validación de tipos después de desserialización",
            "Considerar firmar datos serializados con HMAC",
            "Usar librerías seguras como msgpack o protobuf"
        ]
    },
    
    "path_traversal": {
        "name": "Path Traversal",
        "severity": "high",
        "patterns": [
            r"open\s*\(\s*['\"](?:(?![\s]*['\"])|(?:[^'\"]*\.\./))",
            r"os\.path\.join\s*\(\s*.*\.\./",
            r"(?:pathlib\.Path|Path)\s*\(\s*['\"](?:[^'\"]*\.\./)",
            r"os\.path\.join\s*\(\s*base_dir,\s*(?:user_input|request\.|path\.|filename)",
            r"open\s*\(\s*(?:os\.path\.join|path\.join).*\+\s*(?:request|user|param)",
            r"\.open\s*\(\s*['\"].*\+\s*(?:request\.args|request\.form)",
            r"zipfile\.ZipFile\.extractall\s*\(",
            r"tarfile\.TarFile\.extractall\s*\(",
            r"pathlib\.Path\.read_text\s*\(\s*['\"].*\.\./",
            r"os\.access\s*\(\s*(?:user_path|filename)\s*,",
        ],
        "description": "Acceso a archivos con rutas relativas o sin validación permite path traversal",
        "recommendations": [
            "Validar rutas solicitadas contra whitelist",
            "Usar pathlib.Path.resolve() y verificar que está dentro del directorio permitido",
            "Nunca permitir '..' en rutas de usuario",
            "Usar os.path.commonpath() para validar ruta base",
            "Mantener archivos sensibles fuera del directorio web",
            "Implementar sandboxing de directorios base"
        ]
    },
    
    "insecure_crypto": {
        "name": "Criptografía insegura",
        "severity": "high",
        "patterns": [
            r"hashlib\.md5\s*\(",
            r"hashlib\.sha1\s*\(",
            r"Crypto\.Hash\.MD5\.new\s*\(",
            r"Crypto\.Hash\.SHA\.new\s*\(",
            r"hashlib\.sha256\s*\(\)\.update\s*\(\s*password",
            r"crypt\.crypt\s*\(",
            r"bcrypt\.hashpw\s*\(\s*.*,\s*(?:bcrypt\.gensalt\(\)|bcrypt\.gensalt\(rounds=[0-9]\))",
            r"(?:import|from).*import.*Cipher",
            r"DES\.|DES3|AES\s*\(\s*mode=AES\.MODE_ECB",
            r"random\.choice\s*\(\s*['\"]",
        ],
        "description": "Algoritmos criptográficos débiles (MD5, SHA1, DES) o parámetros inseguros",
        "recommendations": [
            "Usar SHA-256 o SHA-3 en lugar de MD5/SHA1",
            "Usar bcrypt o argon2 para hashear contraseñas (rounds >= 12)",
            "Usar os.urandom() para generar valores aleatorios",
            "Usar cryptography.io para criptografía simétrica (AES-GCM)",
            "Nunca usar DES o Triple DES",
            "Usar librerías modernas como NaCl/libsodium"
        ]
    },
    
    "no_input_validation": {
        "name": "Falta de validación de entrada",
        "severity": "medium",
        "patterns": [
            r"(?:request\.args|request\.form|request\.json|request\.data)\s*\[\s*['\"].*['\"]",
            r"int\s*\(\s*(?:request\.|input\()",
            r"(?:request\.args|request\.form|sys\.argv)\[.*\]\s*(?:\+|-|\*|/|%|==|!=|<|>)",
            r"if\s+(?:request\.args|request\.form|sys\.argv)",
            r"for\s+.+\s+in\s+(?:request\.args|request\.form|request\.json)",
            r"\.split\s*\(\s*(?:request\.args|user_input)",
            r"str\s*\(\s*(?:request\.|sys\.argv)\s*\)",
            r"eval\s*\(\s*(?:request\.args|user_input|sys\.argv)",
            r"use_strict=False[\s\S]*?(?:request\.|parse)",
            r"@app\.route.*def\s+\w+\s*\(\s*\):",
        ],
        "description": "Acceso directo a parámetros de entrada sin validación ni sanitización",
        "recommendations": [
            "Usar Pydantic para validación de modelos",
            "Usar marshmallow para serialización/validación",
            "Usar Cerberus para validación de esquemas",
            "Implementar middleware de validación",
            "Sanitizar todas las entradas del usuario",
            "Usar whitelist de valores permitidos"
        ]
    },
    
    "insecure_dependencies": {
        "name": "Dependencias inseguras",
        "severity": "medium",
        "patterns": [
            r"requests\s*==\s*(?:2\.(?:[0-9]|1[0-9]|2[0-6])|2\.25)",
            r"django\s*==\s*(?:1\.|2\.[0-9]|3\.[0-9]|4\.0)",
            r"flask\s*==\s*(?:0\.|1\.[0-9]|2\.0\.[0-9])",
            r"sqlalchemy\s*==\s*(?:1\.[0-2])",
            r"pyyaml\s*==\s*(?:3\.|4\.|5\.[0-3])",
            r"paramiko\s*==\s*(?:1\.|2\.[0-2])",
            r"jinja2\s*==\s*(?:2\.[0-9]|3\.0\.[0-9])",
            r"cryptography\s*==\s*(?:[0-2]\.)",
            r"pillow\s*==\s*(?:[0-7]\.)",
            r"requirements\.txt.*insecure|requirements\.txt.*--allow-external",
        ],
        "description": "Uso de versiones conocidas de librerías con vulnerabilidades registradas",
        "recommendations": [
            "Actualizar todas las dependencias a versiones seguras",
            "Usar pip-audit para identificar vulnerabilidades",
            "Usar poetry o pipenv para gestión de dependencias",
            "Implementar actualizaciones automáticas con dependabot",
            "Revisar el changelog antes de actualizar",
            "Usar requirements.txt con versiones pinned"
        ]
    },
    
    "xxe_injection": {
        "name": "XML External Entity (XXE) Injection",
        "severity": "high",
        "patterns": [
            r"xml\.etree\.ElementTree\.parse\s*\(",
            r"xml\.dom\.minidom\.parse\s*\(",
            r"xml\.sax\.parse\s*\(",
            r"lxml\.etree\.parse\s*\(",
            r"defusedxml",
            r"XMLParser\s*\(\s*resolve_entities\s*=\s*True",
            r"(?:xml|et|tree)\.fromstring\s*\(\s*(?:request\.|user_input|file_data)",
            r"BeautifulSoup\s*\(\s*.*,\s*['\"]xml['\"]",
            r"untrusted_data[\s\S]*?parse\s*\(",
            r"request\.files\s*\[.*\][\s\S]*?xml\.parse",
        ],
        "description": "Procesamiento de XML con entidades externas habilitadas permite lectura de archivos o DoS",
        "recommendations": [
            "Usar defusedxml en lugar de xml estándar",
            "Deshabilitar DTD y entidades externas en parsers",
            "Usar lxml con xmlschema para validación",
            "Validar y sanitizar entrada XML",
            "Implementar límites en tamaño de archivos",
            "Usar whitelist de elementos XML permitidos"
        ]
    }
}
