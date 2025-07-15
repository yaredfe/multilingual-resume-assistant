# Scripts/parser_helpers.py

import re
import dateparser

def extract_email(text):
    """Extract email addresses from text"""
    try:
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return match.group(0) if match else None
    except Exception as e:
        print(f"ERROR: Error extracting email: {e}")
        return None

def extract_phone(text):
    """Extract phone numbers from text"""
    try:
        # Multiple phone number patterns
        patterns = [
            r"(\+?\d{1,3})?[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}",  # International format
            r"\(\d{3}\)\s?\d{3}-\d{4}",  # US format (555) 123-4567
            r"\d{3}-\d{3}-\d{4}",  # US format 555-123-4567
            r"\d{10}",  # 10 digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    except Exception as e:
        print(f"ERROR: Error extracting phone: {e}")
        return None

def extract_education(text):
    """Extract education information from text"""
    try:
        # Common degree patterns
        degrees = [
            "B.Sc", "M.Sc", "Bachelor", "Master", "B.E", "B.Tech", "PhD", "MBA",
            "Bachelor's", "Master's", "Doctorate", "Associate", "Diploma",
            "B.A", "M.A", "B.S", "M.S", "Ph.D", "D.Phil"
        ]
        
        lines = text.split('\n')
        education = []
        
        for line in lines:
            line_lower = line.lower()
            if any(deg.lower() in line_lower for deg in degrees):
                education.append(line.strip())
        
        return education
    except Exception as e:
        print(f"ERROR: Error extracting education: {e}")
        return []

def extract_experience(text):
    """Extract work experience information from text"""
    try:
        # Keywords that indicate work experience
        experience_keywords = [
            "experience", "developer", "engineer", "manager", "analyst",
            "consultant", "specialist", "coordinator", "assistant", "director",
            "lead", "senior", "junior", "intern", "freelance", "contractor"
        ]
        
        lines = text.split('\n')
        experiences = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in experience_keywords):
                experiences.append(line.strip())
        
        return experiences
    except Exception as e:
        print(f"ERROR: Error extracting experience: {e}")
        return []

def extract_skills(text):
    """Extract technical skills from text"""
    try:
        # Comprehensive list of technical skills
        technical_skills = [
            # Programming Languages
            "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Ruby", "Go", "Rust", "Swift", "Kotlin",
            "Scala", "Perl", "R", "MATLAB", "Julia", "Dart", "Elixir", "Clojure", "Haskell", "Lua",
            
            # Web Technologies
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "Spring",
            "ASP.NET", "Laravel", "Symfony", "Ruby on Rails", "FastAPI", "GraphQL", "REST API",
            
            # Databases
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra", "Oracle", "SQLite", "MariaDB",
            "Neo4j", "Elasticsearch", "DynamoDB", "Firebase", "Supabase",
            
            # Cloud & DevOps
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
            "Terraform", "Ansible", "Chef", "Puppet", "Vagrant", "Vagrant",
            
            # Data Science & ML
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
            "Jupyter", "Apache Spark", "Hadoop", "Kafka", "Airflow", "MLflow", "Kubeflow",
            
            # Mobile Development
            "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic", "Cordova",
            
            # Other Technologies
            "Git", "SVN", "Linux", "Unix", "Windows", "MacOS", "Shell Scripting", "Bash", "PowerShell",
            "Vim", "Emacs", "VS Code", "IntelliJ", "Eclipse", "Xcode", "Android Studio",
            
            # Frameworks & Libraries
            "Bootstrap", "Tailwind CSS", "Sass", "Less", "Webpack", "Babel", "Gulp", "Grunt",
            "Jest", "Mocha", "Chai", "Cypress", "Selenium", "Playwright",
            
            # Methodologies
            "Agile", "Scrum", "Kanban", "Waterfall", "DevOps", "CI/CD", "TDD", "BDD", "DDD"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in technical_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    except Exception as e:
        print(f"ERROR: Error extracting skills: {e}")
        return []

def extract_languages(text):
    """Extract language skills from text"""
    try:
        languages = [
            "English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Chinese",
            "Japanese", "Korean", "Arabic", "Hindi", "Bengali", "Dutch", "Swedish", "Norwegian",
            "Danish", "Finnish", "Polish", "Czech", "Hungarian", "Turkish", "Greek", "Hebrew"
        ]
        
        found_languages = []
        text_lower = text.lower()
        
        for language in languages:
            if language.lower() in text_lower:
                found_languages.append(language)
        
        return found_languages
    except Exception as e:
        print(f"ERROR: Error extracting languages: {e}")
        return []

def extract_certifications(text):
    """Extract certifications from text"""
    try:
        certification_keywords = [
            "certified", "certification", "certificate", "accredited", "licensed",
            "AWS Certified", "Microsoft Certified", "Google Certified", "Cisco Certified",
            "PMP", "PMP®", "PRINCE2", "ITIL", "Scrum Master", "Product Owner"
        ]
        
        lines = text.split('\n')
        certifications = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword.lower() in line_lower for keyword in certification_keywords):
                certifications.append(line.strip())
        
        return certifications
    except Exception as e:
        print(f"ERROR: Error extracting certifications: {e}")
        return []
