CSHARP_VULN_RULES = {
    "sql_injection": {
        "name": "SQL Injection",
        "severity": "critical",
        "patterns": [
            r"command\.CommandText\s*=\s*['\"].*\+",
            r"ExecuteQuery\s*\(\s*['\"].*\+",
            r"@\"SELECT.*\+",
            r"\$\"SELECT.*\{.*\}",
            r"new\s+SqlCommand\s*\(\s*['\"].*\+",
            r"\.Query\s*<.*>\s*\(\s*['\"].*\+",
            r"db\.Database\.ExecuteSqlCommand\s*\(\s*['\"].*\+",
            r"context\.Database\.ExecuteSqlCommand\s*\(\s*userInput",
            r"var\s+query\s*=\s*['\"].*\+\s*(?:user|param|input)",
            r"sql\s*=\s*['\"].*\+\s*\w+",
        ],
        "description": "Concatenación de variables en consultas SQL sin usar parametrización, vulnerables a inyección SQL",
        "recommendations": [
            "Usar SqlParameter para parametrización",
            "Usar LINQ to SQL o Entity Framework con parametrización",
            "Usar Dapper con parametrización",
            "Validar y sanitizar todas las entradas del usuario",
            "Usar whitelist de valores permitidos",
            "Implementar principio de menos privilegios en conexiones DB"
        ]
    },
    
    "command_injection": {
        "name": "Command Injection",
        "severity": "critical",
        "patterns": [
            r"Process\.Start\s*\(\s*['\"]cmd['\"],\s*['\"].*\+",
            r"ProcessStartInfo.*FileName\s*=\s*['\"].*\+",
            r"ProcessStartInfo.*Arguments\s*=\s*['\"].*\+",
            r"new\s+ProcessStartInfo\s*\(\s*['\"].*\+",
            r"cmd\s*\/c\s*.*\+\s*(?:userInput|param)",
            r"bash\s*-c\s*.*\+\s*(?:userInput|param)",
            r"shell.*=.*true[\s\S]*?Process\.Start",
            r"RunAs\s*\(\s*['\"].*\+",
            r"ExecuteAsync\s*\(\s*['\"].*\+",
            r"ShellExecute\s*\(\s*['\"].*\+",
        ],
        "description": "Ejecución de comandos del sistema con variables sin validar, permite command injection",
        "recommendations": [
            "Evitar Process.Start() con string commands concatenados",
            "Usar ProcessStartInfo con lista de argumentos separados",
            "Validar y sanitizar todas las entradas de usuario",
            "Usar whitelist de comandos permitidos",
            "Implementar least privilege para procesos ejecutados",
            "Usar APIs de alto nivel cuando sea posible"
        ]
    },
    
    "hardcoded_secrets": {
        "name": "Secretos hardcodeados",
        "severity": "critical",
        "patterns": [
            r"password\s*=\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"apiKey\s*=\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"api_key\s*=\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"secret\s*=\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"token\s*=\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"connectionString\s*=\s*['\"].*(?:password|pwd).*['\"]",
            r"\"password\"\s*:\s*['\"](?![\s]*['\"])[^'\"]+['\"]",
            r"['\"]Authorization['\"]:\s*['\"]Bearer\s+[^'\"]+['\"]",
            r"AWS_SECRET_ACCESS_KEY\s*=\s*['\"]",
            r"appsettings\.json[\s\S]*?password",
        ],
        "description": "Credenciales, claves API, tokens y secretos expuestos en código fuente",
        "recommendations": [
            "Usar User Secrets para desarrollo local",
            "Usar Azure Key Vault para almacenar secretos",
            "Usar AWS Secrets Manager",
            "Nunca commitar secretos en appsettings.json",
            "Usar configuration managers seguros",
            "Rotar todas las credenciales encontradas inmediatamente"
        ]
    },
    
    "deserialization_vulnerability": {
        "name": "Deserialization Vulnerability",
        "severity": "critical",
        "patterns": [
            r"JsonConvert\.DeserializeObject\s*<.*>\s*\(.*userInput",
            r"BinaryFormatter\.Deserialize\s*\(",
            r"DataContractSerializer\.ReadObject\s*\(",
            r"NetDataContractSerializer\s*\(",
            r"ObjectStateFormatter\.Deserialize\s*\(",
            r"JavaScriptSerializer\.Deserialize\s*\(",
            r"XmlSerializer\.Deserialize\s*\(",
            r"SoapFormatter\.Deserialize\s*\(",
            r"FormatterServices\.GetSafeUninitializedObject",
            r"untrusted[\s\S]*?Deserialize",
        ],
        "description": "Desserialización insegura permite ejecución de código arbitrario",
        "recommendations": [
            "Usar JsonConvert.DeserializeObject con SerializationBinder",
            "Nunca usar BinaryFormatter, NetDataContractSerializer o SoapFormatter",
            "Implementar validación de tipos durante desserialización",
            "Usar Newtonsoft.Json con TypeNameHandling.None",
            "Validar fuente de datos antes de desserializar",
            "Considerar firmar datos serializados con HMAC"
        ]
    },
    
    "xxe_injection": {
        "name": "XML External Entity (XXE) Injection",
        "severity": "high",
        "patterns": [
            r"XmlDocument\s*\(\s*\)",
            r"XmlReaderSettings[\s\S]*?DtdProcessing\s*=\s*DtdProcessing\.Parse",
            r"XDocument\.Load\s*\(\s*(?:userInput|stream|request)",
            r"new\s+XmlTextReader\s*\(\s*(?:userInput|stream)",
            r"XmlSerializer\.Deserialize\s*\(\s*(?:userInput|stream)",
            r"XPathDocument\s*\(\s*(?:userInput|stream)",
            r"XmlReader\.Create\s*\(\s*(?!.*DtdProcessing.*Prohibit)",
            r"<!DOCTYPE[\s\S]*?SYSTEM",
            r"<!ENTITY.*SYSTEM",
            r"ALLOW_EXTERNAL_GENERAL_ENTITIES",
        ],
        "description": "Procesamiento de XML con entidades externas habilitadas permite lectura de archivos o DoS",
        "recommendations": [
            "Establecer DtdProcessing = DtdProcessing.Prohibit",
            "Usar XmlReaderSettings para deshabilitar XXE",
            "Validar y sanitizar entrada XML",
            "Implementar límites en tamaño de archivos",
            "Usar whitelist de elementos XML permitidos",
            "Deshabilitar DOCTYPE declarations"
        ]
    },
    
    "insecure_crypto": {
        "name": "Criptografía insegura",
        "severity": "high",
        "patterns": [
            r"(?:MD5|SHA1)\.Create\s*\(\s*\)",
            r"using.*Cryptography[\s\S]*?MD5|SHA1",
            r"HashAlgorithm\.Create\s*\(\s*['\"]MD5['\"]",
            r"CryptoConfig\.CreateFromName\s*\(\s*['\"]MD5['\"]",
            r"TripleDES\.Create\s*\(\s*\)",
            r"DES\.Create\s*\(\s*\)",
            r"Aes\.Create\s*\(\s*\)[\s\S]*?Mode\s*=\s*CipherMode\.ECB",
            r"RNGCryptoServiceProvider\s*\(\s*new\s+byte\[\]",
            r"Random\s*\(\s*\)\.Next",
            r"System\.Security\.Cryptography\.Rfc2898DeriveBytes\s*\(\s*.*,\s*iterations\s*:\s*[0-9]{1,4}\)",
        ],
        "description": "Algoritmos criptográficos débiles (MD5, SHA1, DES) o parámetros inseguros",
        "recommendations": [
            "Usar SHA256, SHA512 o SHA3 en lugar de MD5/SHA1",
            "Usar Bcrypt o Argon2 para hashear contraseñas",
            "Usar Aes.Create() con modo GCM",
            "Generar IV aleatorios con RNGCryptoServiceProvider",
            "Usar DataProtectionScope.CurrentUser para datos sensibles",
            "Nunca usar DES o TripleDES"
        ]
    },
    
    "path_traversal": {
        "name": "Path Traversal",
        "severity": "high",
        "patterns": [
            r"File\.Open\s*\(\s*userInput",
            r"File\.ReadAllText\s*\(\s*userInput",
            r"File\.WriteAllText\s*\(\s*userInput",
            r"Directory\.GetFiles\s*\(\s*userInput",
            r"Path\.Combine\s*\(\s*baseDir,\s*userInput",
            r"new\s+FileInfo\s*\(\s*userInput",
            r"new\s+DirectoryInfo\s*\(\s*userInput",
            r"StreamReader\s*\(\s*userInput",
            r"StreamWriter\s*\(\s*userInput",
            r"FileStream\s*\(\s*userInput",
        ],
        "description": "Acceso a archivos con rutas relativas o sin validación permite path traversal",
        "recommendations": [
            "Validar rutas solicitadas contra whitelist",
            "Usar Path.GetFullPath() y verificar que está dentro del directorio permitido",
            "Nunca permitir '..' en rutas de usuario",
            "Usar Path.Combine() correctamente",
            "Implementar sandboxing de directorios base",
            "Mantener archivos sensibles fuera del directorio web"
        ]
    },
    
    "weak_authentication": {
        "name": "Autenticación débil",
        "severity": "high",
        "patterns": [
            r"password\.Equals\s*\(",
            r"password\s*==\s*userInput",
            r"password\.CompareTo\s*\(",
            r"MD5\.Create\s*\(\)[\s\S]*?password",
            r"SHA1\.Create\s*\(\)[\s\S]*?password",
            r"Membership\.ValidateUser\s*\(\s*user,\s*password",
            r"FormsAuthentication\.SetAuthCookie",
            r"User\.Identity\.Name\s*==\s*(?:user|userInput)",
            r"\[Authorize\s*\(\s*Roles\s*=\s*['\"].*['\"]",
            r"ValidateUser\s*\(\s*['\"].*['\"],\s*['\"].*['\"]",
        ],
        "description": "Implementación de autenticación débil o validación incorrecta",
        "recommendations": [
            "Usar string.Equals() con StringComparison.Ordinal para datos sensibles",
            "Usar Bcrypt o Argon2 para hashear contraseñas",
            "Implementar ASP.NET Identity para autenticación",
            "Usar JWT tokens con expiración",
            "Implementar rate limiting en intentos de login",
            "Implementar autenticación multifactor (MFA)"
        ]
    },
    
    "insecure_http_headers": {
        "name": "Encabezados HTTP inseguros",
        "severity": "medium",
        "patterns": [
            r"response\.Headers\.Add\s*\(\s*['\"]X-Frame-Options['\"],\s*['\"]['\"]",
            r"response\.Headers\.Add\s*\(\s*['\"]Access-Control-Allow-Origin['\"],\s*['\"]\*['\"]",
            r"response\.Headers\.Add\s*\(\s*['\"]X-Content-Type-Options['\"],\s*['\"].*['\"](?!nosniff)",
            r"enableXssProtection\s*=\s*false",
            r"enableStrictTransportSecurity\s*=\s*false",
            r"response\.Cookies\.Add\s*\(\s*.*HttpOnly\s*=\s*false",
            r"response\.Cookies\.Add\s*\(\s*.*Secure\s*=\s*false",
            r"response\.Headers\.Remove\s*\(\s*['\"]X-Powered-By['\"]",
            r"response\.Headers\[.*\]\s*=\s*['\"]public['\"]",
            r"cacheControl\s*=\s*['\"]public['\"]",
        ],
        "description": "Encabezados HTTP faltantes o mal configurados pueden permitir ataques",
        "recommendations": [
            "Implementar X-Frame-Options: DENY",
            "Implementar X-Content-Type-Options: nosniff",
            "Implementar Strict-Transport-Security",
            "Especificar orígenes permitidos en CORS",
            "Implementar Content-Security-Policy",
            "Usar Secure, HttpOnly en cookies"
        ]
    },
    
    "linq_injection": {
        "name": "LINQ Injection",
        "severity": "high",
        "patterns": [
            r"\.Where\s*\(\s*['\"].*\+.*['\"]",
            r"\.Where\s*\(\s*x\s*=>\s*x\.\w+\.Contains\s*\(\s*userInput",
            r"\.Where\s*\(\s*x\s*=>\s*x\.\w+\s*==\s*userInput",
            r"dynamic\s+.*=.*userInput",
            r"System\.Linq\.Dynamic",
            r"Dynamic.*\.Where\s*\(",
            r"Expression\.Lambda\s*\(\s*.*userInput",
            r"ObjectQuery.*from.*userInput",
            r"EntitySql.*userInput",
            r"\.SqlQuery\s*\(\s*['\"].*\+",
        ],
        "description": "Inyección en consultas LINQ mediante strings concatenados o datos untrusted",
        "recommendations": [
            "Usar LINQ with parametrización",
            "Evitar Dynamic LINQ con entrada del usuario",
            "Usar Expression Trees con validación",
            "Implementar whitelist de campos permitidos",
            "Validar y sanitizar entrada del usuario",
            "Usar ORM con parametrización automática"
        ]
    }
}
