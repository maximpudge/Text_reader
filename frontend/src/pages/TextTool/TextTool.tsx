import { ChangeEvent, useState } from 'react';
import styles from './TextTool.module.css';

const TextTool = () => {
	const [text, setText] = useState<string>('');

	const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
		setText(e.target.value);
	};

	const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (file) {
			const reader = new FileReader();

			reader.onload = (event: ProgressEvent<FileReader>): void => {
				if (event.target?.result && typeof event.target.result === 'string') {
					setText(event.target.result);
				}
			};

			reader.onerror = (): void => {
				console.error('File reading error');
			};

			reader.readAsText(file);
		}
	};

	const handleProceed = () => {
		console.log('Proceeding with text:', text);
	};

	return (
		<div className={styles.text_tool_container}>
			<p className={styles.subtitle}>Введите свой текст или загрузите файл</p>

			<textarea
				className={styles.text_input}
				value={text}
				onChange={handleTextChange}
				placeholder='Введите или вставьте здесь свой текст ...'
			/>

			<div className={styles.buttons_container}>
				<label className={styles.upload_button}>
					Загрузить файл
					<input
						type='file'
						style={{ display: 'none' }}
						onChange={handleFileUpload}
					/>
				</label>
				<button className={styles.proceed_button} onClick={handleProceed}>
					Обработка
				</button>
			</div>
		</div>
	);
};

export default TextTool;
