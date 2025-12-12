import { useEffect } from 'react';
import { App } from 'antd';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { removeNotification } from '@/store/slices/uiSlice';

export const useNotifications = () => {
  const { message } = App.useApp();
  const { notifications } = useAppSelector(state => state.ui);
  const dispatch = useAppDispatch();

  useEffect(() => {
    notifications.forEach(notification => {
      const duration = notification.duration || 3;
      
      message[notification.type]({
        content: notification.message,
        duration,
        onClose: () => {
          dispatch(removeNotification(notification.id));
        },
      });

      // Auto-remove from store after display
      setTimeout(() => {
        dispatch(removeNotification(notification.id));
      }, duration * 1000);
    });
  }, [notifications, message, dispatch]);
};
