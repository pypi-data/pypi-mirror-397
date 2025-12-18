VULN_RULES = {
    "eval_usage": {
        "name": "Uso de eval()",
        "severity": "critical",
        "patterns": [
            r"\beval\s*\(",
            r"\beval\s*\(\s*['\"`]",
            r"\beval\s*\(\s*\$\{",
            r"\bFunction\s*\(\s*['\"`]",
            r"\bsetTimeout\s*\(\s*['\"`]",
            r"\bsetInterval\s*\(\s*['\"`]",
            r"\bsetImmediate\s*\(\s*['\"`]",
            r"new\s+Function\s*\(",
            r"vm\.runInThisContext\s*\(",
            r"vm\.runInNewContext\s*\(",
        ],
        "description": "eval() y funciones similares ejecutan código arbitrario, permiten inyección de código",
        "recommendations": [
            "Nunca utilizar eval() con entrada del usuario",
            "Usar JSON.parse() en lugar de eval() para parsear JSON",
            "Implementar un parser seguro o una DSL interpretada",
            "Considerar usar Web Workers para código aislado",
            "Usar bibliotecas como jexl o expr-eval para expresiones seguras"
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
            r"(?:authorization|auth|AUTHORIZATION)\s*[=:]\s*['\"](?:Bearer|Bearer\s+)[^'\"]+['\"]",
            r"(?:db_password|dbPassword|DB_PASSWORD)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:private_key|privateKey|PRIVATE_KEY)\s*[=:]\s*['\"][\s\S]*?['\"]",
            r"(?:aws_secret|AWS_SECRET|aws_access_key|AWS_ACCESS_KEY)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"(?:stripe_key|stripeKey|STRIPE_KEY)\s*[=:]\s*['\"]sk_(?:test|live)_[^'\"]+['\"]",
            r"(?:mongodb_uri|MONGODB_URI|mongodb_password)\s*[=:]\s*['\"](?![\s]*['\"])[^'\"]*(?:mongodb|password).*['\"]",
        ],
        "description": "Credenciales, claves API, tokens y secretos expuestos en código fuente",
        "recommendations": [
            "Usar variables de entorno (.env) para almacenar secretos",
            "Utilizar gestores de secretos como AWS Secrets Manager o HashiCorp Vault",
            "Nunca commitar archivos .env al repositorio",
            "Implementar .gitignore para excluir archivos con credenciales",
            "Rotar todas las credenciales encontradas inmediatamente",
            "Usar bibliotecas como dotenv para cargar variables de entorno"
        ]
    },
    
    "sql_injection": {
        "name": "SQL Injection",
        "severity": "critical",
        "patterns": [
            r"(?:query|execute|run|db\.(?:query|execute|run))\s*\(\s*['\"`].*(?:\+|\.concat|\.replace|\$\{|\`.*\$\{).*['\"`]",
            r"SELECT\s+.*\+\s*(?:req\.|params\.|query\.)",
            r"INSERT\s+INTO\s+.*\+\s*(?:req\.|params\.|query\.)",
            r"UPDATE\s+.*\+\s*(?:req\.|params\.|query\.)",
            r"DELETE\s+FROM\s+.*\+\s*(?:req\.|params\.|query\.)",
            r"db\.raw\s*\(\s*['\"`].*\+.*['\"`]",
            r"(?:sequelize|knex|typeorm)\.query\s*\(\s*['\"`].*(?:\+|\.concat|\`.*\$\{).*['\"`]",
            r"connection\.query\s*\(\s*['\"`].*(?:\+|\.concat|\$\{|\`.*\$\{).*['\"`]",
            r"mysql\.query\s*\(\s*['\"`].*(?:\+|\.concat|\$\{|\`.*\$\{).*['\"`]",
            r"pool\.query\s*\(\s*['\"`].*(?:\+|\.concat|\$\{|\`.*\$\{).*['\"`]",
        ],
        "description": "Concatenación de variables en consultas SQL sin sanitizar, vulnerables a inyección SQL",
        "recommendations": [
            "Usar prepared statements o parameterized queries",
            "Utilizar ORM como Sequelize, TypeORM o Knex.js",
            "Validar y sanitizar todas las entradas del usuario",
            "Implementar whitelist de valores permitidos",
            "Usar stored procedures en la base de datos",
            "Aplicar principio de menos privilegios en conexiones DB"
        ]
    },
    
    "command_injection": {
        "name": "Command Injection",
        "severity": "critical",
        "patterns": [
            r"(?:exec|execSync|execFile|execFileSync|spawn|spawnSync)\s*\(\s*['\"`].*(?:\+|\.concat|\$\{|\`.*\$\{).*['\"`]",
            r"(?:exec|execSync|execFile)\s*\(\s*`.*\$\{.*\}`",
            r"child_process\.(?:exec|execSync|execFile|spawn)\s*\(\s*(?:cmd|command|args).*(?:\+|\$\{)",
            r"shell\s*:\s*true[\s\S]*?(?:exec|spawn|execFile)\s*\(",
            r"bash\s*-c\s*['\"`].*(?:\+|\$\{).*['\"`]",
            r"/bin/sh\s*-c\s*['\"`].*(?:\+|\$\{).*['\"`]",
            r"(?:require|require\(['\"]child_process['\"])\s*(?:exec|spawn).*\+.*(?:user|input|query|param)",
            r"cp\.execSync\s*\(\s*`.*\$\{",
            r"require\(['\"]child_process['\"]\).*(?:exec|spawn).*\+\s*(?:req\.|params\.|query\.)",
            r"\.exec\s*\(\s*['\"`]\s*.*(?:\+|\.concat|\$\{)",
        ],
        "description": "Ejecución de comandos del sistema con variables sin validar, permite command injection",
        "recommendations": [
            "Evitar exec(), execSync() y spawn() con entrada del usuario",
            "Usar spawn() con array de argumentos en lugar de strings",
            "Nunca pasar shell: true a menos que sea absolutamente necesario",
            "Validar y sanitizar todas las entradas de usuario",
            "Usar whitelist de comandos permitidos",
            "Implementar least privilege para procesos ejecutados"
        ]
    },
    
    "xss_vulnerable": {
        "name": "Cross-Site Scripting (XSS)",
        "severity": "high",
        "patterns": [
            r"\.innerHTML\s*[+=]\s*(?!.*(?:sanitize|escape|DOMPurify))",
            r"\.innerHTML\s*=\s*(?:req\.|query\.|params\.|\.get\(\))",
            r"document\.write\s*\(\s*(?:req\.|query\.|params\.)",
            r"\.insertAdjacentHTML\s*\(\s*['\"]",
            r"dangerouslySetInnerHTML\s*=\s*\{",
            r"v-html\s*=",
            r"ng-bind-html\s*=",
            r"\[\s*innerHTML\s*\]\s*=",
            r"\.html\s*\(\s*(?:req\.|query\.|params\.|\.get\(\))",
            r"\.append\s*\(\s*['\"`].*<.*(?:script|img|svg).*['\"`]",
            r"response\.write\s*\(\s*(?:req\.|query\.|params\.)",
            r"res\.send\s*\(\s*['\"`].*<.*\+\s*(?:req\.|query\.|params\.)",
            r"\.html\s*\(\s*\$\{.*\}\s*\)",
            r"jQuery.*\.html\s*\(\s*(?!.*(?:sanitize|escape))",
        ],
        "description": "Asignación directa de contenido HTML sin sanitizar permite XSS",
        "recommendations": [
            "Usar textContent en lugar de innerHTML cuando sea posible",
            "Sanitizar toda entrada del usuario con DOMPurify",
            "Usar Content Security Policy (CSP) headers",
            "Escapar caracteres especiales (<, >, &, \", ')",
            "Usar plantillas con auto-escape (template literals con librerías)",
            "Implementar X-XSS-Protection headers"
        ]
    },
    
    "insecure_crypto": {
        "name": "Criptografía insegura",
        "severity": "high",
        "patterns": [
            r"(?:crypto\.createHash|createHash)\s*\(\s*['\"](?:md5|sha1)['\"]",
            r"(?:crypto\.createCipher|createCipher)\s*\(",
            r"(?:crypto\.createDecipher|createDecipher)\s*\(",
            r"require\(['\"]md5['\"]\)",
            r"require\(['\"]sha1['\"]\)",
            r"bcrypt\.hash\s*\(\s*[^,]*,\s*[0-9]\s*\)",
            r"crypto\.scrypt\s*\(\s*[^,]*,\s*['\"][a-zA-Z0-9]{1,8}['\"]",
            r"\.hashSync\s*\(\s*[^,]*,\s*[0-9]\s*\)",
            r"crypto\.randomBytes\s*\(\s*(?:1|2|3|4|5)\s*\)",
            r"Math\.random\s*\(\)",
            r"jwt\.sign\s*\(\s*[^,]*,\s*['\"].*['\"]",
            r"jsonwebtoken.*sign.*(?:md5|sha1|['\"]secret['\"])",
        ],
        "description": "Algoritmos criptográficos débiles (MD5, SHA1) o parámetros inseguros",
        "recommendations": [
            "Usar SHA-256 o superior en lugar de MD5/SHA1",
            "Usar bcrypt o scrypt para hashear contraseñas (rounds >= 10)",
            "Usar crypto.createCipheriv en lugar de createCipher",
            "Generar valores aleatorios con crypto.randomBytes()",
            "Usar librerías especializadas para JWT (jsonwebtoken con secretos fuertes)",
            "Implementar key derivation functions (PBKDF2, Argon2)"
        ]
    },
    
    "path_traversal": {
        "name": "Path Traversal",
        "severity": "high",
        "patterns": [
            r"require\s*\(\s*(?:path\.join|__dirname)\s*\+\s*(?:req\.|query\.|params\.)",
            r"fs\.readFile\s*\(\s*(?:path\.|__dirname|\./).*\+\s*(?:req\.|query\.|params\.)",
            r"fs\.readFileSync\s*\(\s*(?:path\.|__dirname|\./).*\+\s*(?:req\.|query\.|params\.)",
            r"fs\.open\s*\(\s*(?:path\.|__dirname|\./).*\+\s*(?:req\.|query\.|params\.)",
            r"fs\.stat\s*\(\s*(?:path\.|__dirname|\./).*\+\s*(?:req\.|query\.|params\.)",
            r"path\.join\s*\(\s*['\"].*['\"],\s*(?:req\.|query\.|params\.)",
            r"require\s*\(\s*['\"].*\.\./",
            r"require\s*\(\s*\`.*\.\./",
            r"import\s+.*from\s+['\"].*\.\./",
            r"sendFile\s*\(\s*(?:req\.|query\.|params\.)",
            r"fs\.readdirSync\s*\(\s*(?:path\.|__dirname)\s*\+\s*(?:req\.|query\.|params\.)",
        ],
        "description": "Acceso a archivos con rutas relativas sin validación permite path traversal",
        "recommendations": [
            "Validar rutas solicitadas contra whitelist",
            "Usar path.resolve() y verificar que está dentro del directorio permitido",
            "Nunca permitir '..' en rutas de usuario",
            "Implementar sandboxing de directorios base",
            "Usar fs.access() antes de leer archivos",
            "Mantener archivos sensibles fuera del directorio web"
        ]
    },
    
    "insecure_dependencies": {
        "name": "Dependencias inseguras",
        "severity": "medium",
        "patterns": [
            r"(?:\"lodash\":|\"lodash\":|'lodash':)\s*['\"][\s\S]*?(?:[0-9]\.){2}[0-9](?:\.[0-9])?['\"]",
            r"(?:\"moment\":|'moment':)\s*['\"](?:2\.1[0-8]|2\.[0-9]\.[0-9])['\"]",
            r"(?:\"jquery\":|'jquery':)\s*['\"](?:1\.|2\.1|3\.[0-2])['\"]",
            r"(?:\"express\":|'express':)\s*['\"](?:[0-3]\.|4\.[0-9]\.[0-9])['\"]",
            r"(?:\"request\":|'request':)",
            r"(?:\"node-uuid\":|'node-uuid':)",
            r"(?:\"ejs\":|'ejs':)\s*['\"](?:[0-2]\.)['\"]",
            r"(?:\"jade\":|'jade':)",
            r"(?:\"npm\":|'npm':)\s*['\"](?:[0-5]\.)['\"]",
            r"(?:\"fs-extra\":|'fs-extra':)\s*['\"](?:[0-2]\.)['\"]",
            r"\"vulnerabilities\"\s*:\s*\[",
        ],
        "description": "Uso de versiones conocidas de librerías con vulnerabilidades registradas",
        "recommendations": [
            "Actualizar todas las dependencias a versiones seguras",
            "Usar npm audit para identificar vulnerabilidades",
            "Implementar npm audit fix regularmente",
            "Usar dependabot o similar para actualizaciones automáticas",
            "Revisar el changelog antes de actualizar",
            "Mantener un registro de dependencias en package.json"
        ]
    },
    
    "no_input_validation": {
        "name": "Falta de validación de entrada",
        "severity": "medium",
        "patterns": [
            r"(?:req\.body|req\.query|req\.params)\.[a-zA-Z_]\w*\s*(?:==|===|\+|-|\/|\*|>|<|\||&|&&)",
            r"\.get\s*\(\s*['\"].*['\"],\s*(?:req\.body|req\.query|req\.params)",
            r"(?:req\.body|req\.query|req\.params)\.[a-zA-Z_]\w*\s*(?:as\s+(?:string|number|int))?(?:\s*[;=+\-*/\|&]|\.)",
            r"if\s*\(\s*(?:req\.body|req\.query|req\.params)\.[a-zA-Z_]\w*\s*\)",
            r"switch\s*\(\s*(?:req\.body|req\.query|req\.params)",
            r"\.find\s*\(\s*(?:req\.body|req\.query|req\.params)\s*\)",
            r"\.filter\s*\(\s*.*(?:req\.body|req\.query|req\.params)",
            r"\.map\s*\(\s*(?:req\.body|req\.query|req\.params)",
            r"\.forEach\s*\(\s*(?:req\.body|req\.query|req\.params)",
            r"const\s+[a-zA-Z_]\w*\s*=\s*(?:req\.body|req\.query|req\.params)\.[a-zA-Z_]\w*(?:;|\s)",
        ],
        "description": "Acceso directo a parámetros de entrada sin validación ni sanitización",
        "recommendations": [
            "Usar librerías de validación como joi, yup o express-validator",
            "Implementar middleware de validación en rutas",
            "Sanitizar todas las entradas del usuario",
            "Usar tipo de datos específicos (parseInt, parseFloat, etc)",
            "Implementar whitelist de valores permitidos",
            "Rechazar valores inesperados o fuera de rango"
        ]
    },
    
    "insecure_cors": {
        "name": "CORS inseguro",
        "severity": "medium",
        "patterns": [
            r"(?:Access-Control-Allow-Origin|origin)\s*[=:]\s*['\"]?\*['\"]?",
            r"cors\s*\(\s*\{\s*origin\s*:\s*\*\s*\}\s*\)",
            r"cors\s*\(\s*\{\s*origin\s*:\s*true\s*\}\s*\)",
            r"cors\s*\(\s*\)\s*(?=;|,|$)",
            r"allowedHeaders\s*[=:]\s*\[?\s*['\"]?\*['\"]?\s*\]?",
            r"exposedHeaders\s*[=:]\s*\[?\s*['\"]?\*['\"]?\s*\]?",
            r"credentials\s*[=:]\s*true[\s\S]*?origin\s*[=:]\s*\*",
            r"\.header\s*\(\s*['\"]Access-Control-Allow-Origin['\"],\s*['\"]?\*['\"]?\s*\)",
            r"res\.header\s*\(\s*['\"]Access-Control-Allow-Origin['\"],\s*['\"]?\*['\"]?\s*\)",
            r"setHeader\s*\(\s*['\"]Access-Control-Allow-Origin['\"],\s*['\"]?\*['\"]?\s*\)",
        ],
        "description": "CORS configurado para permitir cualquier origen (*) permite acceso no autorizado",
        "recommendations": [
            "Especificar orígenes permitidos explícitamente",
            "Usar lista blanca de dominios autorizados",
            "Nunca usar wildcard (*) con credentials: true",
            "Validar origen en cada solicitud",
            "Implementar preflight requests para métodos complejos",
            "Mantener CORS habilitado solo para endpoints que lo necesiten"
        ]
    },
    
    "prototype_pollution": {
        "name": "Prototype Pollution",
        "severity": "high",
        "patterns": [
            r"\.constructor\s*\[.*\]\s*=",
            r"Object\.assign\s*\(\s*\{\}[\s\S]*?(?:req\.body|query|params)",
            r"\.prototype\s*\[.*\]\s*=.*(?:req\.|user\.|input)",
            r"lodash\.merge\s*\(\s*\{\}[\s\S]*?(?:req\.|query\.|params\.)",
            r"JSON\.parse\s*\(\s*.*\)[\s\S]*?\.constructor",
            r"Object\.create\s*\(\s*(?:req\.body|query|params)",
            r"spread operator.*\.\.\.\s*(?:req\.body|query|params)",
            r"\{\s*\.\.\.\s*(?:req\.body|query|params)\s*\}",
            r"for\s*\(\s*.*\s+in\s+(?:req\.body|query|params|obj)\s*\)",
            r"Object\.keys.*\.forEach\s*\([\s\S]*?obj\[.*\]\s*=",
        ],
        "description": "Asignación a propiedades sin validar permite contaminar el prototipo de objetos",
        "recommendations": [
            "Usar Object.hasOwnProperty() para verificar propiedades",
            "Usar Map en lugar de objetos planos cuando sea posible",
            "Validar nombres de propiedades contra whitelist",
            "Usar Object.freeze() para congelar prototipos críticos",
            "Evitar Object.assign() y spread operator con datos untrusted",
            "Usar librerías como lodash con opciones de seguridad habilitadas"
        ]
    }
}
