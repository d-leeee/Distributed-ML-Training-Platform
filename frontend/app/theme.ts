import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    typography: {
        fontSize: 10
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    fontSize: '0.8rem',
                    padding: '2px 8px',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    fontSize: '0.5rem',
                },
            },
        },
        MuiInputBase: {
            styleOverrides: {
                root: {
                    fontSize: '0.6rem',
                },
            },
        },
        // Add more component overrides for smaller boxes if needed
    },
});

export default theme;