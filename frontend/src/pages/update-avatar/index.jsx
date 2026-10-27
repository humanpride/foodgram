import { Container, FormTitle, Main, Form, Button, FileInput } from '../../components'
import styles from './styles.module.css'
import { useContext, useState } from 'react'
import { AuthContext, UserContext } from '../../contexts'
import { Helmet } from 'react-helmet-async'

const UpdateAvatar = ({ onAvatarChange }) => {
  const userContext = useContext(UserContext)

  const [avatarFile, setAvatarFile] = useState(userContext.avatar || null)
  const [updated, setUpdated] = useState(false)

  const checkIfDisabled = () => {
    return avatarFile === '' || avatarFile === null || !updated
  }

  return (
    <Main withBG asFlex>
      <Container className={styles.center}>
        <Helmet>
          <title>Edit avatar</title>
          <meta name="description" content="Foodgram - Edit avatar" />
          <meta property="og:title" content="Edit avatar" />
        </Helmet>

        <Form
          className={styles.form}
          onSubmit={(e) => {
            e.preventDefault()
            if (checkIfDisabled()) {
              return alert('No avatar has been selected or changed')
            }
            onAvatarChange({ file: avatarFile })
          }}
        >
          <FormTitle>Avatar</FormTitle>
          <FileInput
            onChange={(file) => {
              setUpdated(true)
              setAvatarFile(file)
            }}
            fileTypes={["image/png", "image/jpeg"]}
            fileSize={5000}
            className={styles.fileInput}
            file={avatarFile}
          />
          <Button modifier="style_dark" type="submit" className={styles.button}>
            Update avatar
          </Button>
        </Form>
      </Container>
    </Main>
  )
}

export default UpdateAvatar
