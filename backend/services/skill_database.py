"""
Skill Database

Comprehensive database of technical skills for accurate resume parsing.
Only skills in this database will be extracted from resumes.
"""

# Comprehensive skill database organized by category
SKILL_DATABASE = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'cpp', 'csharp',
    'go', 'golang', 'rust', 'kotlin', 'swift', 'php', 'ruby', 'scala', 'r',
    'matlab', 'perl', 'shell', 'bash', 'powershell', 'lua', 'dart', 'elixir',
    'erlang', 'haskell', 'clojure', 'f#', 'fsharp', 'ocaml', 'julia',
    
    # Web Technologies - Frontend
    'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'react', 'reactjs',
    'angular', 'angularjs', 'vue', 'vuejs', 'vue.js', 'next.js', 'nextjs',
    'nuxt.js', 'nuxtjs', 'gatsby', 'svelte', 'ember.js', 'backbone.js',
    'jquery', 'bootstrap', 'tailwind css', 'tailwindcss', 'material-ui', 'mui',
    'ant design', 'chakra ui', 'styled-components', 'webpack', 'vite', 'parcel',
    'rollup', 'babel', 'es6', 'es2015', 'typescript', 'jsx', 'tsx',
    
    # Web Technologies - Backend
    'node.js', 'nodejs', 'express', 'express.js', 'koa', 'nest.js', 'nestjs',
    'django', 'flask', 'fastapi', 'tornado', 'bottle', 'cherrypy', 'pyramid',
    'spring', 'spring boot', 'springboot', 'spring mvc', 'hibernate', 'jpa',
    'asp.net', 'aspnet', '.net', 'dotnet', 'laravel', 'symfony', 'codeigniter',
    'rails', 'ruby on rails', 'sinatra', 'phoenix', 'gin', 'echo', 'fiber',
    'gin framework', 'gin gonic',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis',
    'oracle', 'oracle db', 'sqlite', 'sql server', 'mssql', 'mariadb',
    'cassandra', 'elasticsearch', 'dynamodb', 'couchdb', 'neo4j', 'influxdb',
    'firebase', 'firestore', 'realm', 'supabase', 'prisma', 'sequelize',
    'typeorm', 'sqlalchemy', 'mongoose', 'hibernate', 'jpa',
    
    # Cloud & DevOps
    'aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds', 'dynamodb',
    'cloudfront', 'route53', 'vpc', 'iam', 'cloudformation', 'cloudwatch',
    'azure', 'microsoft azure', 'azure functions', 'azure devops', 'azure ad',
    'gcp', 'google cloud platform', 'google cloud', 'gce', 'gcs', 'cloud functions',
    'docker', 'kubernetes', 'k8s', 'jenkins', 'ci/cd', 'cicd', 'continuous integration',
    'continuous deployment', 'github actions', 'gitlab ci', 'circleci', 'travis ci',
    'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'packer', 'helm',
    'istio', 'linkerd', 'prometheus', 'grafana', 'elk stack', 'elastic stack',
    'splunk', 'datadog', 'new relic', 'cloudwatch', 'azure monitor',
    
    # Version Control & Tools
    'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'perforce',
    'jira', 'confluence', 'trello', 'asana', 'slack', 'microsoft teams',
    
    # Data Science & Machine Learning
    'machine learning', 'ml', 'deep learning', 'dl', 'neural networks', 'cnn',
    'rnn', 'lstm', 'transformer', 'bert', 'gpt', 'tensorflow', 'keras',
    'pytorch', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'scipy',
    'matplotlib', 'seaborn', 'plotly', 'jupyter', 'jupyter notebook',
    'data analysis', 'data science', 'data visualization', 'nlp', 'natural language processing',
    'computer vision', 'opencv', 'image processing', 'time series', 'statistics',
    'apache spark', 'spark', 'hadoop', 'hive', 'pig', 'kafka', 'flink',
    'airflow', 'apache airflow', 'mlflow', 'kubeflow', 'sagemaker',
    
    # Mobile Development
    'android', 'ios', 'react native', 'reactnative', 'flutter', 'dart',
    'xamarin', 'ionic', 'cordova', 'phonegap', 'swift', 'kotlin', 'objective-c',
    'objectivec', 'swiftui', 'uikit', 'android studio', 'xcode',
    
    # Testing
    'unit testing', 'integration testing', 'e2e testing', 'end-to-end testing',
    'jest', 'mocha', 'chai', 'jasmine', 'pytest', 'unittest', 'junit',
    'testng', 'selenium', 'cypress', 'playwright', 'puppeteer', 'appium',
    'postman', 'rest assured', 'karate', 'cucumber', 'gherkin', 'bdd',
    
    # API & Microservices
    'rest api', 'restful api', 'rest', 'graphql', 'grpc', 'soap', 'web services',
    'microservices', 'api development', 'api design', 'openapi', 'swagger',
    'api gateway', 'kong', 'nginx', 'apache', 'load balancing', 'rate limiting',
    
    # Software Engineering Practices
    'agile', 'scrum', 'kanban', 'devops', 'tdd', 'test-driven development',
    'bdd', 'behavior-driven development', 'code review', 'pair programming',
    'continuous integration', 'continuous deployment', 'clean code', 'solid principles',
    'design patterns', 'object-oriented programming', 'oop', 'functional programming',
    'fp', 'mvc', 'mvp', 'mvvm', 'architecture', 'system design', 'distributed systems',
    
    # Operating Systems
    'linux', 'unix', 'windows', 'macos', 'ubuntu', 'centos', 'debian', 'red hat',
    'fedora', 'arch linux', 'windows server', 'powershell', 'bash scripting',
    
    # Other Tools & Technologies
    'elasticsearch', 'kibana', 'logstash', 'rabbitmq', 'apache kafka', 'kafka',
    'apache nifi', 'nifi', 'apache storm', 'storm', 'apache flink', 'flink',
    'nginx', 'apache http server', 'tomcat', 'jetty', 'wildfly', 'jboss',
    'redis', 'memcached', 'varnish', 'cdn', 'content delivery network',
}

# Skill aliases - map common variations to canonical names
SKILL_ALIASES = {
    'node.js': 'nodejs',
    'node': 'nodejs',
    'react.js': 'react',
    'reactjs': 'react',
    'vue.js': 'vue',
    'vuejs': 'vue',
    'next.js': 'nextjs',
    'nuxt.js': 'nuxtjs',
    'asp.net': 'aspnet',
    '.net': 'dotnet',
    'c++': 'cpp',
    'c#': 'csharp',
    'f#': 'fsharp',
    'postgresql': 'postgres',
    'mongodb': 'mongo',
    'kubernetes': 'k8s',
    'machine learning': 'ml',
    'deep learning': 'dl',
    'natural language processing': 'nlp',
    'react native': 'reactnative',
    'objective-c': 'objectivec',
    'rest api': 'rest',
    'restful api': 'rest',
    'amazon web services': 'aws',
    'google cloud platform': 'gcp',
    'microsoft azure': 'azure',
    'ci/cd': 'cicd',
    'continuous integration': 'cicd',
    'test-driven development': 'tdd',
    'behavior-driven development': 'bdd',
    'object-oriented programming': 'oop',
    'functional programming': 'fp',
}

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to match database format.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Normalized skill name (lowercase, no extra spaces)
    """
    if not skill:
        return ""
    
    # Convert to lowercase and strip
    skill = skill.lower().strip()
    
    # Remove common prefixes
    skill = skill.replace('knowledge of', '').replace('experience with', '')
    skill = skill.replace('proficient in', '').replace('skilled in', '')
    skill = skill.replace('expert in', '').replace('familiar with', '')
    
    # Remove special characters except spaces and hyphens
    import re
    skill = re.sub(r'[^\w\s-]', '', skill)
    
    # Normalize whitespace
    skill = re.sub(r'\s+', ' ', skill).strip()
    
    # Check aliases
    if skill in SKILL_ALIASES:
        skill = SKILL_ALIASES[skill]
    
    return skill

def is_valid_skill(skill: str) -> bool:
    """
    Check if a skill exists in the database.
    
    Args:
        skill: Skill name to check
        
    Returns:
        True if skill is in database, False otherwise
    """
    normalized = normalize_skill(skill)
    return normalized in SKILL_DATABASE

def get_canonical_skill_name(skill: str) -> str:
    """
    Get the canonical (display) name for a skill.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Canonical skill name for display, or None if not found
    """
    normalized = normalize_skill(skill)
    
    if normalized in SKILL_DATABASE:
        # Return a nicely formatted version
        # Capitalize first letter of each word
        words = normalized.split()
        return ' '.join(word.capitalize() for word in words)
    
    return None
