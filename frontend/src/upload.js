import React from "react";
import "./upload.css";

class UploadFile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { file: "", msg: "", jobID: "", key: "" };
  }

  onFileChange = (event) => {
    this.setState({
      file: event.target.files[0],
    });
  };

  resetFileInput() {
    let randomString = Math.random().toString(36);

    this.setState({ key: randomString });
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  uploadFileData = (event) => {
    let fetchResult = (JobID) => {
      console.log("firing api with JobID: " + JobID);
      fetch("http://127.0.0.1:5000/download/" + JobID).then((res) => {
        if (res.status === 202) {
          this.setState({ msg: "Processing..." });
          this.sleep(2000).then(() => fetchResult(this.state.jobID));
        } else if (res.status === 200) {
          this.setState({ msg: "Downloading file" });
          //   fetch("http://127.0.0.1:5000/download/" + JobID);
          window.location.href = "http://127.0.0.1:5000/download/" + JobID;
          this.sleep(2000).then(() => {
            this.setState({ file: "", msg: "Ready", jobID: "" });
            this.resetFileInput();
          });
          // let blob = res.blob();
          // const url = window.URL.createObjectURL(new Blob([blob]));
          // const link = document.createElement("a");
          // link.href = url;
          // link.setAttribute("download", "subtitle.srt");
          // document.body.appendChild(link);
          // link.click();
          // link.parentNode.removeChild(link);
        }
      });
    };

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
        this.setState({ jobID: json.message });
        console.log(this.state.jobID);
      })
      .then(() => {
        fetchResult(this.state.jobID);
      });
  };

  render() {
    return (
      <div id="container">
        <h1>Auto Subitlte Created by Firstzazx</h1>
        <h3>Upload a File (Only wav)</h3>
        <h4>Status: {this.state.msg}</h4>
        <input
          onChange={this.onFileChange}
          type="file"
          key={this.state.key || ""}
        />
        <button disabled={!this.state.file} onClick={this.uploadFileData}>
          Upload
        </button>
      </div>
    );
  }
}

export default UploadFile;
