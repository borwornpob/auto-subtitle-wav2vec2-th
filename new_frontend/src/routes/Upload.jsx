import { useState } from "react";
import {
  Button,
  Input,
  Text,
  Container,
  VStack,
  Heading,
  Center,
} from "@chakra-ui/react";

import useWindowDimensions from "../hooks/dimensions";

export default function Upload() {
  const [file, setFile] = useState("");
  const [msg, setMsg] = useState("");
  const [jobId, setJobId] = useState("");
  const [key, setKey] = useState("");
  const [data, setData] = useState();

  const { width, height } = useWindowDimensions();

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const resetFileInput = () => {
    let randomString = Math.random().toString(36);

    setKey(randomString);
  };

  const sleep = (milliseconds) => {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  };

  const onFileUpload = async () => {
    if (!file) {
      setMsg("Please select a file to upload");
      return;
    } else {
      const formData = new FormData();
      formData.append("file", file);

      await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        body: formData,
        mode: "cors",
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          fetchResult(data.message);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  };

  const fetchResult = async (jobId) => {
    console.log("firing api with job id: ", jobId);
    fetch("http://127.0.0.1:5000/download/" + jobId)
      .then((res) => {
        if (res.status === 202) {
          setMsg("Turning your wav into Thai Subitles");
          sleep(2000).then(() => {
            fetchResult(jobId);
          });
        } else if (res.status === 200) {
          setMsg("Your Subtitles are ready!");
          window.open("http://127.0.0.1:5000/download/" + jobId, "_blank");
          sleep(2000).then(() => {
            setMsg("");
            setFile("");
            setJobId("");
            resetFileInput();
          });
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Container centerContent width={width}>
      <Heading fontSize="4xl" mt={2}>
        Thai Subtitle Generator
      </Heading>
      <Text fontSize="2xl">Upload your wav file</Text>
      <VStack spacing={4}>
        <Input
          type={"file"}
          key={key}
          onChange={onFileChange}
          accept="audio/wav"
          p={1}
        />
        <Button onClick={onFileUpload} color="teal" width="100%">
          Upload
        </Button>
        <Text>Status: {msg}</Text>
      </VStack>
    </Container>
  );
}
