import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Form.css"

function Voter({ route, method }) {
    const [election, setElection] = useState(0);
    const [auth, setAuth] = useState(0);
    const [candidate, setCandidate] = useState(0);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();


    const getVoter = () => {
        api
            .get("/api/voter/")
            .then((res) => res.data)
            .then((data) => {
                setNotes(data);
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

    return (
        <div>
            <div>
                <h2>Home page</h2>
            </div>
            <h2>Register in election</h2>
            <form onSubmit={registerVoter}>
                <br />
                <input
                    type="int"
                    id="election"
                    name="Election ID"
                    required
                    onChange={(e) => setElection(e.target.value)}
                    value={election}
                />
                <br />
                <input type="submit" value="Submit"></input>
            </form>
        </div>
    )

}

export default Voter