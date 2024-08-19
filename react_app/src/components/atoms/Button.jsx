import React from 'react';
import './Button.scss';
const Button = ({ label, onClick, variant }) => (
<button className={`button ${variant}`} onClick={onClick}>
   {label}
</button>
);
export default Button;