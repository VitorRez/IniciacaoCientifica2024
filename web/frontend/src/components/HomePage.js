import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Form, Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";

export default class HomePage extends Component {
    constructor(props){
        super(props);
        this.state = {
            name: "",
            cpf: "",
            electionid: "",
        };

        this.handleNameChange = this.handleNameChange.bind(this);
        this.handleCpfChange = this.handleCpfChange.bind(this);
        this.handleElectionIdChange = this.handleElectionIdChange.bind(this);
        this.handleAccessButtonPressed = this.handleAccessButtonPressed.bind(this);
    }

    handleNameChange(e) {
        this.setState({
            name: e.target.value,
        });
    }

    handleCpfChange(e) {
        this.setState({
            cpf: e.target.value,
        });
    }

    handleElectionIdChange(e) {
        this.setState({
            electionid: e.target.value,
        });
    }

    handleAccessButtonPressed() {
        /*const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                name: this.state.name,
                cpf: this.state.cpf,
                electionid: this.state.electionid,
            }),
        };*/
        console.log(this.state)
    }

    render() {
        return(
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography component="h2" variant="h2">
                        Access The Voting Plataform
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField
                        required={true}
                        type="text"
                        onChange={this.handleNameChange}
                        ></TextField>
                        <FormHelperText>
                            <div align="center">Name</div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField
                        required={true}
                        type="text"
                        onChange={this.handleCpfChange}
                        ></TextField>
                        <FormHelperText>
                            <div align="center">CPF</div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField
                        required={true}
                        type="text"
                        onChange={this.handleElectionIdChange}
                        ></TextField>
                        <FormHelperText>
                            <div align="center">Election ID</div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" onClick={this.handleAccessButtonPressed}>Enter</Button>
                </Grid>
            </Grid>
        );
    }
}