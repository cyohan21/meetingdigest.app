import axios from "axios";

const instance = axios.create({
  baseURL: "http://localhost:1011/", // Replace with your Flask backend URL
  withCredentials: true, // ⬅️ Needed to send/receive httpOnly cookies
});

export default instance;