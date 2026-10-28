import { useState, useEffect, useRef } from 'react'
import styles from './styles.module.css'
import { Button } from '../index'
import cn from 'classnames'
import Icons from '../icons'
import DefaultImage from "../../images/userpic-icon.jpg"

const FileInput = ({
  label,
  onChange,
  file = null,
  className,
  fileSize,
  fileTypes
}) => {
  const [ currentFile, setCurrentFile ] = useState(file)
  const fileInput = useRef(null)

  useEffect(_ => {
    if (file !== currentFile) {
      setCurrentFile(file)
    }
  }, [file])

  const getBase64 = (file) => {
    const reader = new FileReader()

    if (fileSize && ((file.size / 1000) > fileSize)) {
      return alert(`Upload a file no larger than ${fileSize / 1000}MB`)
    }
    if (fileTypes && !fileTypes.includes(file.type)) {
      return alert(`Upload a file of one of these types: ${fileTypes.join(', ')}`)
    }
    reader.readAsDataURL(file);
    reader.onload = function () {
      setCurrentFile(reader.result)
      onChange(reader.result)
    };
    reader.onerror = function (error) {
      console.log('Error: ', error);
    }
  }

  return <div className={cn(styles.container, className)}>
    {label && <label className={styles.label}>
      {label}
    </label>}
    <input
      className={styles.fileInput}
      type='file'
      ref={fileInput}
      onChange={e => {
        const file = e.target.files[0]
        getBase64(file)
      }}
    />
    <Button
      clickHandler={_ => {
        fileInput.current.click()
      }}
      className={styles.button}
      type='button'
    >
      Choose file
    </Button>
    {currentFile && <div
      className={styles.image}
      style={{
        backgroundImage: `url(${currentFile})`
      }}
      onClick={() => {
        onChange(null)
        setCurrentFile(null)
        fileInput.current.value = null
      }}
    >
      <div className={styles.imageOverlay}>
        <Icons.ReceiptDelete />
      </div>
    </div>}
  </div>
}

export default FileInput
