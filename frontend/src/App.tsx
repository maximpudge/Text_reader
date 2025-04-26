import Footer from './components/Footer/Footer';
import Header from './components/Header/Header';
import { useTextStore } from './model/textStore';
import TextTool from './pages/TextTool/TextTool';

import styles from './App.module.css';

function App() {
	const { resultData } = useTextStore();
	return (
		<>
			<Header />
			<main>
				<TextTool />

				<div className={styles.text}>
					{resultData && <pre>{JSON.stringify(resultData, null, 3)}</pre>}
				</div>
			</main>
			<Footer />
		</>
	);
}

export default App;
