import { create, StateCreator } from 'zustand';

type TextState = {
	text: string;
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
