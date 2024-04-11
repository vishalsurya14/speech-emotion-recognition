import unittest
from flask import Flask
from app import app  # Assuming your Flask app instance is named 'app'

class TestSpeechEmotionRecognition(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_file_not_found(self):
        response = self.app.post('/realtimeprediction', data=dict(file=("invalid_audio.wav", open("nonexistent_file.wav", "rb"))))
        self.assertIn(b'FileNotFoundError', response.data)

    def test_successful_prediction(self):
        # Provide a valid audio file for which the model is trained
        # Adjust the file path and name accordingly
        with open("valid_audio.wav", "rb") as valid_audio:
            response = self.app.post('/realtimeprediction', data=dict(file=("valid_audio.wav", valid_audio)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Prediction:', response.data)

    def test_invalid_audio_file(self):
        # Provide an invalid audio file (unsupported format or incorrect data)
        with open("invalid_audio.mp3", "rb") as invalid_audio:
            response = self.app.post('/realtimeprediction', data=dict(file=("invalid_audio.mp3", invalid_audio)))
        self.assertIn(b'Invalid file format', response.data)

    def test_login(self):
        response = self.app.post('/', data=dict(email="valid_email@example.com", password="valid_password"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully', response.data)

    def test_invalid_login(self):
        response = self.app.post('/', data=dict(email="invalid_email@example.com", password="invalid_password"))
        self.assertIn(b'Please enter correct email / password', response.data)

    def test_register_existing_user(self):
        response = self.app.post('/register', data=dict(name="ExistingUser", email="existing@example.com", password="existing_password"))
        self.assertIn(b'Account already exists', response.data)

    def test_register_invalid_email(self):
        response = self.app.post('/register', data=dict(name="InvalidEmail", email="invalid_email", password="password"))
        self.assertIn(b'Invalid email address', response.data)

    def tearDown(self):
        pass  # Clean up if needed

if __name__ == '__main__':
    unittest.main()
