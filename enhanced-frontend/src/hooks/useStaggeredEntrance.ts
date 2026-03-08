import { useState, useEffect } from 'react'

interface StaggeredEntranceReturn {
  isVisible: boolean
  containerVariants: {
    hidden: { opacity: number }
    visible: { opacity: number; transition: { staggerChildren: number; delayChildren: number } }
    exit: { opacity: number; transition: { staggerChildren: number; staggerDirection: number } }
  }
  itemVariants: {
    hidden: { opacity: number; y: number; scale: number }
    visible: { opacity: number; y: number; scale: number; transition: { duration: number; ease: string | number[] } }
    exit: { opacity: number; y: number; scale: number; transition: { duration: number; ease: string | number[] } }
  }
  titleVariants: {
    hidden: { opacity: number; x: number }
    visible: { opacity: number; x: number; transition: { duration: number; ease: string | number[] } }
    exit: { opacity: number; x: number; transition: { duration: number; ease: string | number[] } }
  }
}

export const useStaggeredEntrance = (
  _itemCount: number | number[],
  staggerDelay: number = 0.1,
  initialDelay: number = 0.2
): StaggeredEntranceReturn => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, initialDelay * 1000)

    return () => clearTimeout(timer)
  }, [initialDelay])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: 0.1,
      },
    },
    exit: {
      opacity: 0,
      transition: {
        staggerChildren: staggerDelay,
        staggerDirection: -1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: [0.4, 0, 0.2, 1],
      },
    },
    exit: {
      opacity: 0,
      y: -20,
      scale: 0.95,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 1, 1],
      },
    },
  }

  const titleVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.6,
        ease: [0.4, 0, 0.2, 1],
      },
    },
    exit: {
      opacity: 0,
      x: 20,
      transition: {
        duration: 0.4,
        ease: [0.4, 0, 1, 1],
      },
    },
  }

  return {
    isVisible,
    containerVariants,
    itemVariants,
    titleVariants,
  }
}
