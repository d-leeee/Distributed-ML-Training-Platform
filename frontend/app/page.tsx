import Container from '@mui/material/Container';
import JobSubmitter from './components/job_submitter/job_submitter';

export default function Home() {
  return (
    <div>
      <Container maxWidth="xs">
        <JobSubmitter />
      </Container>
    </div>
  );
}