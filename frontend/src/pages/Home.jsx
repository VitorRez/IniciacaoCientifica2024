import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { jwtDecode } from "jwt-decode";
import "../styles/Home.css"


function isTokenExpired(token) {
    if (!token) return true;
    const { exp } = jwtDecode(token);
    const now = Date.now().valueOf() / 1000;
    return exp < now;
}

async function refreshToken() {
    try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);

        const response = await fetch('http://localhost:8000/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        localStorage.setItem(ACCESS_TOKEN, data.access);
        return data.access;
    } catch (error) {
        console.error('Error refreshing token:', error);
        return null;
    }
}

async function postData(route, data) {
    console.log(data)
    try {
        let accessToken = localStorage.getItem(ACCESS_TOKEN);
        
        if (isTokenExpired(accessToken)) {
            accessToken = await refreshToken();
            if (!accessToken) {
                throw new Error('Could not refresh token');
            }
        }

        const response = await fetch(route, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            console.log(response)
            alert('Invalid password.')
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        console.log('Success:', result);
        alert('Voter authenticated!')
    } catch (error) {
        console.error('Error:', error);
    }
}

function Voter({ route, method }) {
    const [auth, setAuth] = useState(0);
    const [candidate, setCandidate] = useState(0);
    const [password, setPassword] = useState("");
    const [officei, setOffice] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const authenticateVoter = (e) => {
        e.preventDefault();
        postData("http://127.0.0.1:8000/api/voter-authentication/", password)
    }

    const applyCandidate = (e) => {
        e.preventDefault();
        postData("http://127.0.0.1:8000/api/apply/", password)
    }

    return (
        <div id="frame">
            <br></br>
            <div>
                <h2>Home page</h2>
            </div>
            <h2>Authenticate in election</h2>
            <form onSubmit={authenticateVoter}>
                <h4>Password:</h4>
                <input
                    type="password"
                    id="password"
                    name="password"
                    onChange={(e) => setPassword(e.target.value)}
                    required
                ></input>
                <input type="submit" value="Submit"></input>
            </form>
            <br/>
            <h2>Apply for office</h2>
            <form onSubmit={applyCandidate}>
                <h4>Type office ID:</h4>
                <input
                    type="int"
                    id="office"
                    name="Office"
                    required
                ></input>
                <input type="submit" value="Submit"></input>
            </form>
            <br/>
        </div>
    )
}

export default Voter