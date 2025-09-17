import Processor from "./components/processor";
import Input from "./components/input";
import Container from '@mui/material/Container';

export default function Home() {
  return (
    <div>
      <Container maxWidth="xs">
        <Input />
      </Container>
    </div>
  );
}