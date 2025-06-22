import {BrowserRouter as Router, Routes, Route } from "react-router-dom"
import './App.css'
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import Register from "./pages/Register"
import Upload from "./pages/Login"

function App() {

  return (
    <>
      <Router>
        <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/upload" element={<Upload />} />
        </Routes>
      </Router>
    </>
  )
}

export default App
