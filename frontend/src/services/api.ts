import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:5000/api", // Replace with your Flask backend URL
  withCredentials: true, // ⬅️ Needed to send/receive httpOnly cookies
});

export default instance;