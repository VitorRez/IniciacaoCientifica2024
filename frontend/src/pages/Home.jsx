import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Home.css"

function Voter({ route, method }) {
    const [voter, setVoter] = useState([])
    const [election, setElection] = useState(0);
    const [auth, setAuth] = useState(0);
    const [candidate, setCandidate] = useState(0);
    const [password, setPassword] = useState("");
    const [officei, setOffice] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();


    const getVoter = () => {
        api
            .get("/api/voter/")
            .then((res) => res.data)
            .then((data) => {
                setVoter(data);
                console.log(data);
            })
            .catch((err) => alert(err));
    }

    const registerVoter = (e) => {
        e.preventDefault();
        api
            .post("/api/voter/", { election, auth, candidate })
            .then((res) => {
                if (res.status === 201) alert("Voter created!");
                else alert("Failed to make voter.");
                getVoter();
            })
            .catch((err) => alert(err));
    }

    const registerElection = (e) => {
        e.preventDefault();
        api
            .post("/api/register-election/", { election })
            .then((res) => {
                if (res.status === 201) alert("Voter registered!");
                else alert("Failed to register voter.");
                getVoter();
            })
            .catch((err) => alert(err));
    }

    const authenticateVoter = (e) => {
        e.preventDefault();
        api
            .post("/api/voter-authentication/")
            .then((res) => {
                if (res.status === 201) alert("Voter authenticated!");
                else alert("Failed to authenticate voter.");
                getVoter();
            })
            .catch((err) => alert(err));
    }

    const applyCandidate = (e) => {
        e.preventDefault();
        api
            .post("/api/apply/")
            .then((res) => {
                if (res.status === 201) alert("Candidate registered!");
                else alert("Failed to register candidate.");
                getVoter();
            })
            .catch((err) => alert(err));
    }

    return (
        <div id="frame">
            <br></br>
            <div>
                <h2>Home page</h2>
            </div>
            <button onClick={(e) => registerVoter}>CreateVoter</button>
            <h2>Register in election</h2>
            <form onSubmit={registerElection}>
                <h4>Type Election ID:</h4>
                <input
                    type="int"
                    id="election"
                    name="Election ID"
                    placeholder="Election ID"
                    required
                    onChange={(e) => setElection(e.target.value)}
                    value={election}
                />
                <input type="submit" value="Submit"></input>
            </form>
            <h2>Authenticate in election</h2>
            <form onSubmit={authenticateVoter}>
                <h4>Password:</h4>
                <input
                    type="password"
                    id="password"
                    name="Password"
                    required
                    onChange={(e) => authenticateVoter(e.target.value)}
                    value={password}
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