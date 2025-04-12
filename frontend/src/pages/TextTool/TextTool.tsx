import { ChangeEvent } from 'react';
import styles from './TextTool.module.css';
import { useTextStore } from '../../model/textStore';

const PROCESSOR_TYPES = ['tokenize', 'lemmatize', 'paraphrase'];
const METHODS = ['spacy', 'nltk', 'simple'];
const LANGUAGES = ['ru', 'en'];

const TextTool = () => {
	const {
		text,
		setText,
		language,
		setLanguage,
		processorType,
		setProcessorType,
		methods,
		setMethods,
		return_pos,
		return_entities,
		return_mapping,
		return_original,
		setChecked,
	} = useTextStore();

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
		console.dir({
			language,
			methods,
			processorType,
			return_entities,
			return_mapping,
			return_original,
			return_pos
		})
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

			<div className={styles.select_method}>
				<label className={styles.label_text} htmlFor='languages'>
					Выберете язык:
				</label>
				<select
					name='languages'
					id='languages'
					onChange={e => setLanguage(e.target.value)}
				>
					{LANGUAGES.length &&
						LANGUAGES.map(item => (
							<option key={item} value={item}>
								{item}
							</option>
						))}
				</select>
			</div>

			<div className={styles.select_method}>
				<label className={styles.label_text} htmlFor='tokenizator'>
					Выберете обработчик:
				</label>
				<select
					name='tokenizator'
					id='tokenizator'
					onChange={e => setProcessorType(e.target.value)}
				>
					{PROCESSOR_TYPES.length &&
						PROCESSOR_TYPES.map(item => (
							<option key={item} value={item}>
								{item}
							</option>
						))}
				</select>
			</div>

			<div className={styles.select_method}>
				<label className={styles.label_text} htmlFor='methods'>
					Выберете метод:
				</label>
				<select
					name='methods'
					id='methods'
					onChange={e => setMethods(e.target.value)}
				>
					{METHODS.length &&
						METHODS.map(item => (
							<option key={item} value={item}>
								{item}
							</option>
						))}
				</select>
			</div>

			<div className={styles.checkboxes}>
				<div className={styles.select_method}>
					<label htmlFor='pos'>return_pos</label>
					<input
						type='checkbox'
						id='pos'
						name='pos'
						checked={return_pos}
						onChange={e => setChecked('return_pos', e.target.checked)}
					/>
				</div>

				<div className={styles.select_method}>
					<label htmlFor='entities'>return_entities</label>
					<input
						type='checkbox'
						id='entities'
						name='entities'
						checked={return_entities}
						onChange={e => setChecked('return_entities', e.target.checked)}
					/>
				</div>

				<div className={styles.select_method}>
					<label htmlFor='mapping'>return_mapping</label>
					<input
						type='checkbox'
						id='mapping'
						name='mapping'
						checked={return_mapping}
						onChange={e => setChecked('return_mapping', e.target.checked)}
					/>
				</div>

				<div className={styles.select_method}>
					<label htmlFor='original'>return_original</label>
					<input
						type='checkbox'
						id='original'
						name='original'
						checked={return_original}
						onChange={e => setChecked('return_original', e.target.checked)}
					/>
				</div>
			</div>

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
