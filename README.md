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
flowchart TD

    A[AI CV Scanner for Hiring Managers]

    subgraph B[resume_evaluator/]
        B1[flask_app.py<br/>Flask backend]
        B2[model_handling.py<br/>AI logic]
        B3[requirements.txt]

        subgraph C[static/]
            C1[css/style.css<br/>Custom styling]
            C2[js/script.js<br/>Interactive behavior]
            C3[logo.png<br/>bitskraft.com logo]
        end

        subgraph D[templates/]
            D1[index.html<br/>Main page]
            D2[results.html<br/>Results page]
        end

        subgraph E[uploads/]
            E1[resumes/<br/>Temp storage (optional)]
        end
    end

    %% Connections
    A --> B
    B1 --> D1
    B1 --> D2
    B2 --> B1
    C1 --> D1
    C2 --> D1
    C3 --> D1
    E1 --> B1
