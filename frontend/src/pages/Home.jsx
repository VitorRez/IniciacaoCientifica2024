import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import "../styles/Home.css";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";

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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        localStorage.setItem(ACCESS_TOKEN, data.access);
        return data.access;
    } catch (error) {
        console.error('Error refreshing token:', error);
        return null;
    }
}

async function postData(route, data, ok_message, error_message) {
    console.log(data);
    try {
        let accessToken = localStorage.getItem(ACCESS_TOKEN);
        if (isTokenExpired(accessToken)) {
            accessToken = await refreshToken();
            if (!accessToken) throw new Error('Could not refresh token');
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
            console.log(response.body);
            alert(error_message);
            throw new Error('Network response was not ok');
        }
        const result = await response.json();
        console.log('Success:', result);
        alert(ok_message);
    } catch (error) {
        console.error('Error:', error);
    }
}

function Voter() {
    const [password, setPassword] = useState("");
    const [officeid, setOffice] = useState("");
    const [campaignid, setCampaignid] = useState("");
    const [offices, setOffices] = useState([]);
    const [election, setElection] = useState("");
    const [elections, setElections] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchElections() {
            const accessToken = localStorage.getItem(ACCESS_TOKEN);
            const response = await fetch(`http://127.0.0.1:8000/api/elections/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setElections(data.data);
            } else {
                console.error('Failed to fetch elections.');
            }
        }
    
        fetchElections();
    }, []);

    useEffect(() => {
        async function fetchOffices() {
            if (election) {
                const accessToken = localStorage.getItem(ACCESS_TOKEN);
                const response = await fetch(`http://127.0.0.1:8000/api/offices/?electionid=${election}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setOffices(data.data);
                } else {
                    console.error('Failed to fetch offices.');
                }
            }
        }

        fetchOffices();
    }, [election]);

    const authenticateVoter = (e) => {
        e.preventDefault();
        postData("http://127.0.0.1:8000/api/voter-authentication/", { password, election }, 'Voter authenticated!', 'Invalid password.');
    };

    const applyCandidate = (e) => {
        e.preventDefault();
        postData("http://127.0.0.1:8000/api/apply/", { password, election, officeid, campaignid }, 'Voter registered as candidate!', 'Voter not authenticated or invalid password.');
    };

    return (
        <div id="frame">
            <br />
            <div>
                <h2>Home page</h2>
            </div>
            <h2>Authenticate in election</h2>
            <form onSubmit={authenticateVoter}>
                <h4>Election:</h4>
                <select
                    id="election"
                    name="Election"
                    onChange={(e) => setElection(e.target.value)}
                    required
                >
                    <option value="">Select an election</option>
                    {elections.map((election) => (
                        <option key={election.electionid} value={election.electionid}>
                            {election.electionid}
                        </option>
                    ))}
                </select>
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
            <br />
            <h2>Apply for office</h2>
            <form onSubmit={applyCandidate}>
                <h4>Election:</h4>
                <select
                    id="election"
                    name="Election"
                    onChange={(e) => setElection(e.target.value)}
                    required
                >
                    <option value="">Select an election</option>
                    {elections.map((election) => (
                        <option key={election.electionid} value={election.electionid}>
                            {election.electionid}
                        </option>
                    ))}
                </select>
                <h4>Office:</h4>
                <select
                    id="office"
                    name="Office"
                    onChange={(e) => setOffice(e.target.value)}
                    required
                >
                    <option value="">Select an office</option>
                    {offices.map((office) => (
                        <option key={office.id} value={office.id}>
                            {office.name}
                        </option>
                    ))}
                </select>
                <h4>Campaign ID:</h4>
                <input
                    type="int"
                    id="campaign"
                    name="Campaign"
                    onChange={(e) => setCampaignid(e.target.value)}
                    required
                ></input>
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
            <br />
        </div>
    );
}

export default Voter;
