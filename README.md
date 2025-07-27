# Commons Swipe - Instagram-like Wikimedia Commons Browser

A modern, Instagram-style web application for browsing Wikimedia Commons images with user authentication and social features.

## Features

- **Image Browsing**: Swipe through Wikimedia Commons images like Instagram
- **Google OAuth**: Secure user authentication with Google accounts
- **User Interactions**: Like, favorite, and comment on images
- **User Profiles**: View your liked, favorited, and commented images
- **Search**: Search for specific images on Wikimedia Commons
- **Categories**: Browse images by different categories
- **Responsive Design**: Works on desktop and mobile devices

## Setup

### Prerequisites

- Python 3.7+
- Google OAuth credentials

### Installation

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Set authorized redirect URI to `http://localhost:5000/authorize`

4. Set environment variables (optional, defaults provided):
   ```bash
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export FLASK_SECRET_KEY="your-secret-key"
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`

3. Click "Login" to authenticate with Google

## Usage

### Browsing Images
- Swipe up/down or use arrow keys to navigate between images
- Click the heart icon to like an image
- Click the star icon to favorite an image
- Click the comment icon to add a comment

### Search
- Use the search bar to find specific images
- Search results will display in the same swipe interface

### Categories
- Click the "Categories" button to browse by category
- Select different categories to see related images

### Profile
- Click "Profile" in the header to view your interactions
- See all your liked, favorited, and commented images

## API Endpoints

- `POST /api/interact` - Save user interactions (like, favorite, comment)
- `GET /api/user/interactions` - Get user's interactions
- `GET /profile` - User profile page
- `GET /login` - Google OAuth login
- `GET /logout` - Logout user

## Database

The application uses SQLite with the following models:
- `User`: Stores user information from Google OAuth
- `UserInteraction`: Stores user likes, favorites, and comments

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Authlib
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite
- **Authentication**: Google OAuth 2.0
- **Image Source**: Wikimedia Commons API

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 