import { create, StateCreator } from 'zustand';

type TextState = {
	text: string;
	resultData: any;
	status?: 'pending' | 'loading' | 'completed';
	language?: 'ru' | 'en';
	processorType?: 'tokenize' | 'lemmatize' | 'paraphrase';
	methods?: 'spacy' | 'nltk' | 'simple';
	return_pos: boolean;
	return_entities: boolean;
	return_mapping: boolean;
	return_original: boolean;
};

type TextActions = {
	setText: (text: string) => void;
	setResultData: (resultData: any) => void;
	setStatus: (status: 'pending' | 'loading' | 'completed') => void;
	setLanguage: (text: 'ru' | 'en') => void;
	setProcessorType: (text: 'tokenize' | 'lemmatize' | 'paraphrase') => void;
	setMethods: (text: 'spacy' | 'nltk' | 'simple') => void;
	setChecked: (
		key:
			| 'return_pos'
			| 'return_entities'
			| 'return_mapping'
			| 'return_original',
		value: true | false
	) => void;
};

const textSlice: StateCreator<TextState & TextActions> = set => ({
	resultData: null,
	text: '',
	language: 'ru',
	processorType: 'tokenize',
	methods: 'spacy',
	return_pos: false,
	return_entities: false,
	return_mapping: false,
	return_original: false,
	setText: (text: string) => {
		set({ text });
	},
	setStatus: (status: 'pending' | 'loading' | 'completed') => {
		set({ status });
	},
	setResultData: (resultData: any) => {
		set({ resultData });
	},
	setLanguage: (text: 'ru' | 'en') => {
		set({ language: text });
	},
	setProcessorType: (text: 'tokenize' | 'lemmatize' | 'paraphrase') => {
		set({ processorType: text });
	},
	setMethods: (text: 'spacy' | 'nltk' | 'simple') => {
		set({ methods: text });
	},
	setChecked: (
		key:
			| 'return_pos'
			| 'return_entities'
			| 'return_mapping'
			| 'return_original',
		value: true | false
	) => {
		set({ [key]: value });
	},
});

export const useTextStore = create<TextState & TextActions>(textSlice);
