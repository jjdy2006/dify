import type { FC } from 'react'
import { useState } from 'react'
import {
  RiDeleteBinLine,
  RiEditLine,
} from '@remixicon/react'
import { useDebounceFn } from 'ahooks'
import { useContext } from 'use-context-selector'
import { useTranslation } from 'react-i18next'
import { useStore as useTagStore } from './store'
import Confirm from '@/app/components/base/confirm'
import cn from '@/utils/classnames'
import type { Tag } from '@/app/components/base/tag-management/constant'
import { ToastContext } from '@/app/components/base/toast'
import {
  deleteTag,
  updateTag,
} from '@/service/tag'

type TagItemEditorProps = {
  tag: Tag
}
const TagItemEditor: FC<TagItemEditorProps> = ({
  tag,
}) => {
  const { t } = useTranslation()
  const { notify } = useContext(ToastContext)
  const tagList = useTagStore(s => s.tagList)
  const setTagList = useTagStore(s => s.setTagList)

  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(tag.name)
  const editTag = async (tagID: string, name: string) => {
    if (name === tag.name) {
      setIsEditing(false)
      return
    }
    if (!name) {
      notify({ type: 'error', message: 'tag name is empty' })
      setName(tag.name)
      setIsEditing(false)
      return
    }
    try {
      const newList = tagList.map((tag) => {
        if (tag.id === tagID) {
          return {
            ...tag,
            name,
          }
        }
        return tag
      })
      setTagList([
        ...newList,
      ])
      setIsEditing(false)
      await updateTag(tagID, name)
      notify({ type: 'success', message: t('common.actionMsg.modifiedSuccessfully') })
      setName(name)
    }
    catch (e: any) {
      notify({ type: 'error', message: t('common.actionMsg.modifiedUnsuccessfully') })
      setName(tag.name)
      const recoverList = tagList.map((tag) => {
        if (tag.id === tagID) {
          return {
            ...tag,
            name: tag.name,
          }
        }
        return tag
      })
      setTagList([
        ...recoverList,
      ])
      setIsEditing(false)
    }
  }
  const [showRemoveModal, setShowRemoveModal] = useState(false)
  const [pending, setPending] = useState<boolean>(false)
  const removeTag = async (tagID: string) => {
    if (pending)
      return
    try {
      setPending(true)
      await deleteTag(tagID)
      notify({ type: 'success', message: t('common.actionMsg.modifiedSuccessfully') })
      const newList = tagList.filter(tag => tag.id !== tagID)
      setTagList([
        ...newList,
      ])
      setPending(false)
    }
    catch (e: any) {
      notify({ type: 'error', message: t('common.actionMsg.modifiedUnsuccessfully') })
      setPending(false)
    }
  }
  const { run: handleRemove } = useDebounceFn(() => {
    removeTag(tag.id)
  }, { wait: 200 })

  return (
    <>
      <div className={cn('shrink-0 flex items-center gap-0.5 pr-1 pl-2 py-1 rounded-lg border border-components-panel-border text-sm leading-5 text-text-secondary')}>
        {!isEditing && (
          <>
            <div className='text-sm leading-5 text-text-secondary'>
              {tag.name}
            </div>
            <div className='shrink-0 px-1 text-sm leading-4.5 text-text-tertiary font-medium'>{tag.binding_count}</div>
            <div className='group/edit shrink-0 p-1 rounded-md cursor-pointer hover:bg-state-base-hover' onClick={() => setIsEditing(true)}>
              <RiEditLine className='w-3 h-3 text-text-tertiary group-hover/edit:text-text-secondary' />
            </div>
            <div className='group/remove shrink-0 p-1 rounded-md cursor-pointer hover:bg-state-base-hover' onClick={() => {
              if (tag.binding_count)
                setShowRemoveModal(true)
              else
                handleRemove()
            }}>
              <RiDeleteBinLine className='w-3 h-3 text-text-tertiary group-hover/remove:text-text-secondary' />
            </div>
          </>
        )}
        {isEditing && (
          <input
            className='shrink-0 outline-none appearance-none placeholder:text-text-quaternary caret-primary-600'
            autoFocus
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && editTag(tag.id, name)}
            onBlur={() => editTag(tag.id, name)}
          />
        )}
      </div>
      <Confirm
        title={`${t('common.tag.delete')} "${tag.name}"`}
        isShow={showRemoveModal}
        content={t('common.tag.deleteTip')}
        onConfirm={() => {
          handleRemove()
          setShowRemoveModal(false)
        }}
        onCancel={() => setShowRemoveModal(false)}
      />
    </>
  )
}

export default TagItemEditor
