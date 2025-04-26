import { ChangeEvent } from 'react';
import styles from './TextTool.module.css';
import { useTextStore } from '../../model/textStore';
import axios from 'axios';

const PROCESSOR_TYPES = ['tokenize', 'lemmatize', 'paraphrase'];
const METHODS = ['spacy', 'nltk', 'simple'];
const LANGUAGES = ['ru', 'en'];

interface TextResponse {
	status: 'success' | 'failed';
	text_id: string;
}

interface ProcessRequest {
	text_id: string;
	processing_type: string;
	parameters: {
		method: string;
		language: string;
		return_pos: boolean;
		return_entities: boolean;
		return_mapping: boolean;
		return_original: boolean;
	};
}

interface TaskStatus {
	status: string;
	result?: {
		text_id: string;
		processing_type: string;
	};
}

interface ProcessingResults {
	[key: string]: any;
}

const sleep = (ms: number): Promise<void> => {
	return new Promise(resolve => setTimeout(resolve, ms));
};

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
		setResultData,
		status,
		setStatus,
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

	const handleProceed = async (): Promise<void> => {
		try {
			setResultData(null)
			setStatus('pending');
			setStatus('loading');
			const { data }: { data: TextResponse } = await axios.post(
				'http://localhost:8000/text',
				{ text }
			);

			if (data.status === 'success') {
				const processData: ProcessRequest = {
					text_id: data.text_id,
					processing_type: processorType as
						| 'tokenize'
						| 'lemmatize'
						| 'paraphrase',
					parameters: {
						method: methods as 'spacy' | 'nltk' | 'simple',
						language: language as 'ru' | 'en',
						return_pos: return_pos,
						return_entities: return_entities,
						return_mapping: return_mapping,
						return_original: return_original,
					},
				};

				const { data: processTextData } = await axios.post<{ task_id: string }>(
					'http://localhost:8000/process',
					processData
				);

				await sleep(3000);

				const { data: taskStatus } = await axios.get<TaskStatus>(
					`http://localhost:8000/task/${processTextData.task_id}`
				);

				if (taskStatus.status === 'completed') {
					const { data: result } = await axios.get<ProcessingResults>(
						`http://localhost:8000/text/${taskStatus.result.text_id}/result/${taskStatus.result.processing_type}`
					);

					setStatus('completed');
					setResultData(result);
				}
			}

			console.log('Proceeding with text:', text);
			console.dir({
				language,
				methods,
				processorType,
				return_entities,
				return_mapping,
				return_original,
				return_pos,
			});
		} catch (error) {
			console.error('Error in handleProceed:', error);
			throw error;
		}
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
				{status === 'pending' || status === 'loading' ? (
					<button className={styles.loading_button} disabled={true}>
						Загрузка...
					</button>
				) : (
					<button className={styles.proceed_button} onClick={handleProceed}>
						Обработка
					</button>
				)}
			</div>
		</div>
	);
};

export default TextTool;
