import React from 'react';
import styles from './Footer.module.css';

const Footer = () => {
	return (
		<footer className={styles.footer}>
			<p>© 2025 TextTool. Все права защищены.</p>
			<div className={styles.footer_links}>
				<a href='/privacy'>Политика конфиденциальности</a>
				<a href='/terms'>Условия обслуживания</a>
				<a href='/contact'>Связаться с нами</a>
			</div>
		</footer>
	);
};

export default Footer;
