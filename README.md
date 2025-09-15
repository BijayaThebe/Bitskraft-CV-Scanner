# Bitskraft-CV-Scanner
AI cv Scanner for Hiring Managers

resume_evaluator/

│

├── flask_app.py                     # Flask backend

├── model_handling.py                # AI logic (from earlier)

├── requirements.txt

│

├── static/

│   ├── css/

│   │   └── style.css              # Custom styling

│   ├── js/

│   │   └── script.js              # Interactive behavior

│   └── logo.png                   # bitskraft.com logo

│

├── templates/

│   ├── index.html                 # Main page

│   └── results.html               # Results page

│

└── uploads/

   └── resumes/                   # Temp storage (optional)


# Files and Folder Hierarchy
```mermaid
graph TD
    A[Bitskraft-CV-Scanner] --> B[resume_evaluator]
    B --> C[flask_app.py]
    B --> D[model_handling.py]
    B --> E[requirements.txt]
    B --> F[static]
    B --> G[templates]
    B --> H[uploads]
    F --> I[css]
    F --> J[js]
    F --> K[logo.png]
    I --> L[style.css]
    J --> M[script.js]
    G --> N[index.html]
    G --> O[results.html]
    H --> P[resumes]
```


