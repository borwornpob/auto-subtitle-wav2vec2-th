import React from "react";
import "./upload.css";

class UploadFile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { file: "", msg: "" };
  }

  onFileChange = (event) => {
    this.setState({
      file: event.target.files[0],
    });
  };

  uploadFileData = (event) => {
    event.preventDefault();
    this.setState({ msg: "" });

    let data = new FormData();
    data.append("file", this.state.file);

    fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      mode: "cors",
      body: data,
    })
      .then((res) => res.json())
      .then((json) => {
        this.setState({ msg: json.message });
      });
  };

  render() {
    return (
      <div id="container">
        <h1>File Upload Example using React</h1>
        <h3>Upload a File</h3>
        <h4>Job-id: {this.state.msg}</h4>
        <input onChange={this.onFileChange} type="file"></input>
        <button disabled={!this.state.file} onClick={this.uploadFileData}>
          Upload
        </button>
      </div>
    );
  }
}

export default UploadFile;
