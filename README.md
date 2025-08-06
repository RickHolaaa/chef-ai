# Chef AI

## 📌 Context

Chef AI is an innovative application designed to assist users in identifying ingredients and generating recipes using advanced machine learning models. This project is developed as part of the Microsoft Azure course at EPITA.

The project is composed of three components:
- **Frontend**: User interface for interaction.
- **Custom Vision**: Local version downloaded from the website.
- **Machine Learning**: Currently unavailable due to Azure account expiration.

## 🛠️ Features

- **Ingredient Recognition**: Upload an image to identify ingredients using a trained machine learning model.
- **Recipe Suggestions**: Generate recipes based on identified ingredients.
- **Manual Ingredient Selection**: Select ingredients manually to generate recipes.

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RickHolaaa/chef-ai.git
   ```
2. Navigate to the project directory:
   ```bash
   cd chef-ai
   ```

## 🖥️​ Usage

1. Start the application:
   ```bash
   docker compose up -d
   ```
2. Access the web interface at `http://localhost:5000`.
3. Upload an image or manually select ingredients to generate recipes.

## 🧪 Technologies Used

- **Custom Vision**: Local version downloaded from the website.
- **Python**: Backend development.
- **HTML/CSS**: Frontend design.
- **Docker**: Containerization.
